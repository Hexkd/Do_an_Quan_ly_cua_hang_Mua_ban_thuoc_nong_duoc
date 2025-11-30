"""
Module để điều khiển form quản lý Sản phẩm
Chứa class Controller_formSanPham.
"""

from PyQt6 import QtWidgets, QtCore, QtSql
 
class Controller_formSanPham:
    """Điều khiển form Sản Phẩm"""
    def __init__(self, parent_window, ui_sanpham, db):
        self.parent_window = parent_window
        self.ui = ui_sanpham
        self.db = db
        self._table_model = None    # QSqlTableModel (SanPham) -> để insert/update/delete
        self._current_row = -1
        self._is_adding = False
        self._is_editing = False
        self._setup_ui()
        self._setup_su_kien()

    def _tao_model_sp(self, table_name, headers):
        """Tạo QSqlTableModel cho SanPham (sử dụng khi cần submit qua model)."""
        if self.db is None or not self.db.isOpen():
            return None
        model = QtSql.QSqlTableModel(parent=self.parent_window, db=self.db)
        model.setTable(table_name)
        model.setEditStrategy(QtSql.QSqlTableModel.EditStrategy.OnManualSubmit)
        model.select()
        for idx, h in enumerate(headers):
            model.setHeaderData(idx, QtCore.Qt.Orientation.Horizontal, h)
        return model

    def _setup_ui(self):
        """Thiết lập giao diện ban đầu; hiển thị dữ liệu lên tbvSanPham"""
        # Lấy bảng SanPham từ CSDL và đặt các tên cột
        self._table_model = self._tao_model_sp("SanPham", ["Mã SP", "Tên SP", "Giá", "Số lượng"])
        if self._table_model is None:
            return
        self.ui.tbvSanPham.setModel(self._table_model)
        self.ui.tbvSanPham.resizeColumnsToContents()
        self.ui.tbvSanPham.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.ui.tbvSanPham.setSelectionMode(QtWidgets.QTableView.SelectionMode.SingleSelection)

        # Thiết lập trạng thái control ban đầu
        self._bat_tat_control(False)

    def _setup_su_kien(self):
        """Kết nối các sự kiện"""
        self.ui.tbvSanPham.selectionModel().currentChanged.connect(self._chon_dong_sp)
        self.ui.btnThem.clicked.connect(self._them_sp)
        self.ui.btnSua.clicked.connect(self._sua_sp)
        self.ui.btnXoa.clicked.connect(self._xoa_sp)
        self.ui.btnLuu.clicked.connect(self._luu_sp)
        self.ui.btnHuy.clicked.connect(self._huy_them_sua_sp)
        self.ui.btnThoat.clicked.connect(self.parent_window.close)

    def _bat_tat_control(self, enable=False):
        """Bật/tắt controls của form Sản Phẩm.
        - True :
            + ON : Lưu, Hủy, ô nhập
            + OFF: ...
        - False:
            + ON : Thêm, Sửa, Xóa
            + OFF: ...
        """

        self.ui.txtMaSP.setReadOnly(not enable)
        self.ui.txtTenSP.setReadOnly(not enable)
        self.ui.txtGia.setReadOnly(not enable)
        self.ui.txtSoLuong.setReadOnly(not enable)

        self.ui.btnThem.setEnabled(not enable)
        self.ui.btnSua.setEnabled(not enable)
        self.ui.btnXoa.setEnabled(not enable)
        self.ui.btnLuu.setEnabled(enable)
        self.ui.btnHuy.setEnabled(enable)

    def _lam_moi_models(self):
        """Làm mới lại model"""
        query = QtSql.QSqlQuery(self.db)
        query.prepare("SELECT MaSP, TenSP, Gia, SoLuong FROM SanPham")
        query.exec()
        self._model.setQuery(query)

    def _sp_ton_tai(self, ma_sp):
        """Kiểm tra Mã SP đã tồn tại trong SanPham không."""
        if not ma_sp:
            return False
        qry = QtSql.QSqlQuery(self.db)
        qry.prepare("SELECT MaSP FROM SanPham WHERE MaSP = :masp")
        qry.bindValue(":masp", ma_sp)
        if not qry.exec():
            return False
        return qry.next()

    def _chon_dong_sp(self, current_index, previous_index):
        """Xử lý khi chọn dòng trong tbvSanPham (dùng view_model index)."""
        if self._is_adding:
            return
        row = current_index.row()
        if row < 0 or self._table_model is None or row >= self._table_model.rowCount():
            return
        ma_sp = self._table_model.data(self._table_model.index(row, 0))
        ten_sp = self._table_model.data(self._table_model.index(row, 1))
        gia = self._table_model.data(self._table_model.index(row, 2))
        sl = self._table_model.data(self._table_model.index(row, 3))

        self.ui.txtMaSP.setText(str(ma_sp))
        self.ui.txtTenSP.setText(str(ten_sp))
        self.ui.txtGia.setText(str(gia))
        self.ui.txtSoLuong.setText(str(sl))

        self._current_row = row

    def _them_sp(self):
        """Thêm Sản phẩm."""
        self._is_adding = True
        self._is_editing = False

        self.ui.txtMaSP.clear()
        self.ui.txtTenSP.clear()
        self.ui.txtGia.clear()
        self.ui.txtSoLuong.clear()
        self._bat_tat_control(True)
        self.ui.txtMaSP.setFocus()

    def _sua_sp(self):
        """Sửa Sản phẩm."""
        row = self._current_row
        if row < 0:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng chọn sản phẩm để sửa.")
            return
        self._is_adding = False
        self._is_editing = True
        self._bat_tat_control(True)
        self.ui.txtMaSP.setFocus()

    def _xoa_sp(self):
        """Xóa Sản phẩm (chặn xóa nếu MaSP đang được tham chiếu trong HoaDon)"""
        row = self._current_row
        if row < 0:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng chọn sản phẩm để xóa.")
            return

        masp = self.ui.txtMaSP.text().strip()
        if not masp:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Mã sản phẩm không hợp lệ.")
            return

        # Kiểm tra tham chiếu trong HoaDon
        qry_check = QtSql.QSqlQuery(self.db)
        qry_check.prepare("SELECT 1 FROM HoaDon WHERE MaSP = :masp LIMIT 1")
        qry_check.bindValue(":masp", masp)
        if not qry_check.exec():
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi kiểm tra ràng buộc: {qry_check.lastError().text()}")
            return
        if qry_check.next():
            QtWidgets.QMessageBox.warning(self.parent_window, "Không thể xóa", "Sản phẩm đang được tham chiếu trong hóa đơn, không thể xóa.")
            return

        reply = QtWidgets.QMessageBox.question(
            self.parent_window,
            "Xác nhận",
            f"Bạn có chắc muốn xóa sản phẩm '{masp}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        # Xóa trong transaction
        try:
            # Bắt đầu transaction
            self.db.transaction()
            qry_del = QtSql.QSqlQuery(self.db)
            qry_del.prepare("DELETE FROM SanPham WHERE MaSP = :masp")
            qry_del.bindValue(":masp", masp)
            # Nếu xóa thất bại -> rollback
            if not qry_del.exec():
                self.db.rollback()
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Xóa thất bại: {qry_del.lastError().text()}")
                return
            #! Commit transaction
            self.db.commit()
        except Exception as ex:
            self.db.rollback()
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi khi xóa: {ex}")
            return

        # Reset UI và làm mới bảng
        self._lam_moi_models()
        self._current_row = -1
        self.ui.txtMaSP.clear()
        self.ui.txtTenSP.clear()
        self.ui.txtGia.clear()
        self.ui.txtSoLuong.clear()

    def _luu_sp(self):
        """Lưu Sản phẩm (thêm hoặc sửa)"""
        masp = self.ui.txtMaSP.text().strip()
        tensp = self.ui.txtTenSP.text().strip()
        gia_str = self.ui.txtGia.text().strip()
        sl_str = self.ui.txtSoLuong.text().strip()

        if not masp or not tensp or not gia_str or not sl_str:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return
        try:
            gia = int(gia_str)
            if gia < 0:
                QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Giá phải lớn hơn hoặc bằng 0.")
                return
        except Exception:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Giá không hợp lệ.")
            return

        try:
            so_luong = int(sl_str)
            if so_luong < 0:
                QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Số lượng phải lớn hơn hoặc bằng 0.")
                return
        except Exception:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Số lượng không hợp lệ.")
            return

        # Nếu thêm, kiểm tra MaSP đã tồn tại chưa
        if self._is_adding:
            qry_check = QtSql.QSqlQuery(self.db)
            qry_check.prepare("SELECT 1 FROM SanPham WHERE MaSP = :masp LIMIT 1")
            qry_check.bindValue(":masp", masp)
            if not qry_check.exec():
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi kiểm tra mã: {qry_check.lastError().text()}")
                return
            if qry_check.next():
                QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Mã sản phẩm đã tồn tại.")
                return

            # Thực hiện Thêm SP
            try:
                self.db.transaction()
                qry_insert = QtSql.QSqlQuery(self.db)
                qry_insert.prepare("""
                    INSERT INTO SanPham (MaSP, TenSP, Gia, SoLuong)
                    VALUES (:masp, :tensp, :gia, :sl)
                """)
                qry_insert.bindValue(":masp", masp)
                qry_insert.bindValue(":tensp", tensp)
                qry_insert.bindValue(":gia", gia)
                qry_insert.bindValue(":sl", so_luong)
                if not qry_insert.exec():
                    self.db.rollback()
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lưu thất bại: {qry_insert.lastError().text()}")
                    return
                self.db.commit()
                QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Thêm sản phẩm thành công.")
            except Exception as ex:
                self.db.rollback()
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi: {ex}")
                return

        if self._is_editing:
            # Thực hiện Sửa SP
            try:
                self.db.transaction()
                qry_update = QtSql.QSqlQuery(self.db)
                qry_update.prepare("""
                    UPDATE SanPham SET TenSP = :tensp, Gia = :gia, SoLuong = :sl
                    WHERE MaSP = :masp
                """)
                qry_update.bindValue(":tensp", tensp)
                qry_update.bindValue(":gia", gia)
                qry_update.bindValue(":sl", so_luong)
                qry_update.bindValue(":masp", masp)
                if not qry_update.exec():
                    self.db.rollback()
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Cập nhật thất bại: {qry_update.lastError().text()}")
                    return
                self.db.commit()
                QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Cập nhật sản phẩm thành công.")
            except Exception as ex:
                self.db.rollback()
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi: {ex}")
                return

        self._lam_moi_models()
        self._is_adding = False
        self._bat_tat_control(False)

    def _huy_them_sua_sp(self):
        """Hủy thao tác Thêm/Sửa; phục hồi dữ liệu hiển thị."""
        if self._is_adding:
            self.ui.txtMaSP.clear()
            self.ui.txtTenSP.clear()
            self.ui.txtGia.clear()
            self.ui.txtSoLuong.clear()
        else:
            row = self._current_row
            if row >= 0 and row < self._model.rowCount():
                self.ui.txtMaSP.setText(str(self._model.data(self._model.index(row, 0))))
                self.ui.txtTenSP.setText(str(self._model.data(self._model.index(row, 1))))
                self.ui.txtGia.setText(str(self._model.data(self._model.index(row, 2))))
                self.ui.txtSoLuong.setText(str(self._model.data(self._model.index(row, 3))))
        self._is_adding = False
        self._is_editing = False
        self._bat_tat_control(False)