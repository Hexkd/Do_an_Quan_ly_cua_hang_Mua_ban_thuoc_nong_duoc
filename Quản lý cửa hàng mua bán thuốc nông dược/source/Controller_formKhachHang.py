"""
Module để điều khiển form quản lý Khách hàng
Chứa class Controller_formKhachHang.
"""

from PyQt6 import QtWidgets, QtCore, QtSql


class Controller_formKhachHang:
    """Điều khiển form Khách Hàng"""
    def __init__(self, parent_window, ui_khachhang, db):
        self.parent_window = parent_window
        self.ui = ui_khachhang
        self.db = db
        self._table_model = None   # QSqlTableModel -> để insert/update/delete
        self._view_model = None    # QSqlQueryModel -> hiển thị kèm tổng số hóa đơn / tổng tiền
        self._current_row = -1
        self._is_adding = False
        self._is_editing = False
        self._sua_ma_goc = None
        self._setup_ui()
        self._setup_su_kien()

    def _tao_model_kh_table(self, table_name, headers):
        """Tạo QSqlTableModel thao tác cho bảng KhachHang"""
        if self.db is None or not self.db.isOpen():
            return None
        model = QtSql.QSqlTableModel(parent=self.parent_window, db=self.db)
        model.setTable(table_name)
        model.setEditStrategy(QtSql.QSqlTableModel.EditStrategy.OnManualSubmit)
        model.select()
        for idx, h in enumerate(headers):
            model.setHeaderData(idx, QtCore.Qt.Orientation.Horizontal, h)
        return model

    def _tao_model_kh_view(self):
        """Tạo QSqlQueryModel hiển thị:
        - Hiển thị bảng KhachHang
        - Tổng số hóa đơn
        - Tổng số tiền đã thanh toán"""
        if self.db is None or not self.db.isOpen():
            return None
        model = QtSql.QSqlQueryModel(parent=self.parent_window)
        qry = QtSql.QSqlQuery(self.db)
        qry.prepare("""
            SELECT kh.MaKH, kh.TenKH, kh.SDT,
                   COUNT(hd.MaHD) AS SoHoaDon,
                   COALESCE(SUM(hd.ThanhTien), 0) AS TongTien
            FROM KhachHang kh
            LEFT JOIN HoaDon hd ON kh.MaKH = hd.MaKH
            GROUP BY kh.MaKH, kh.TenKH, kh.SDT
            ORDER BY kh.MaKH
        """)
        if not qry.exec():
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi truy vấn: {qry.lastError().text()}")
            return None
        model.setQuery(qry)
        headers = ["Mã KH", "Tên KH", "SĐT", "Tổng số hóa đơn", "Tổng số tiền đã thanh toán"]
        for idx, h in enumerate(headers):
            model.setHeaderData(idx, QtCore.Qt.Orientation.Horizontal, h)
        return model

    def _setup_ui(self):
        """Thiết lập giao diện ban đầu"""
        self._table_model = self._tao_model_kh_table("KhachHang", ["Mã KH", "Tên KH", "Số điện thoại"])
        self._view_model = self._tao_model_kh_view()
        if self._view_model is None or self._table_model is None:
            return

        # Hiển thị view model lên table view
        self.ui.tbvKhachHang.setModel(self._view_model)
        self.ui.tbvKhachHang.resizeColumnsToContents()
        self.ui.tbvKhachHang.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.ui.tbvKhachHang.setSelectionMode(QtWidgets.QTableView.SelectionMode.SingleSelection)

        # Thiết lập trạng thái control ban đầu
        try:
            self._bat_tat_control(False)
            self.ui.btnSua.setEnabled(False)
            self.ui.btnXoa.setEnabled(False)
            self.ui.btnLuu.setEnabled(False)
            self.ui.btnHuy.setEnabled(False)
        except Exception:
            pass

    def _setup_su_kien(self):
        """Kết nối các sự kiện"""
        self.ui.tbvKhachHang.selectionModel().currentChanged.connect(self._chon_dong_kh)
        self.ui.btnThem.clicked.connect(self._them_kh)
        self.ui.btnSua.clicked.connect(self._sua_kh)
        self.ui.btnXoa.clicked.connect(self._xoa_kh)
        self.ui.btnLuu.clicked.connect(self._luu_kh)
        self.ui.btnHuy.clicked.connect(self._huy_them_sua_kh)
        self.ui.btnThoat.clicked.connect(self.parent_window.close)

    def _bat_tat_control(self, enable=False):
        """Bật/tắt controls của form Nhân Viên.
        - True :
            + ON : Lưu, Hủy, ô nhập
            + OFF: ...
        - False:
            + ON : Thêm, Sửa, Xóa
            + OFF: ...
        """
        self.ui.txtMaKH.setReadOnly(not enable)
        self.ui.txtTenKH.setReadOnly(not enable)
        self.ui.txtSDT.setReadOnly(not enable)

        self.ui.btnThem.setEnabled(not enable)
        self.ui.btnSua.setEnabled(not enable)
        self.ui.btnXoa.setEnabled(not enable)
        self.ui.btnLuu.setEnabled(enable)
        self.ui.btnHuy.setEnabled(enable)

    def _lam_moi_models(self):
        """Làm mới cả table_model và view_model."""
        if self._table_model:
            self._table_model.select()
        if self._view_model:
            qry = QtSql.QSqlQuery(self.db)
            qry.prepare("""
                SELECT kh.MaKH, kh.TenKH, kh.SDT,
                       COUNT(hd.MaHD) AS SoHoaDon,
                       COALESCE(SUM(hd.ThanhTien), 0) AS TongTien
                FROM KhachHang kh
                LEFT JOIN HoaDon hd ON kh.MaKH = hd.MaKH
                GROUP BY kh.MaKH, kh.TenKH, kh.SDT
                ORDER BY kh.MaKH
            """)
            qry.exec()
            self._view_model.setQuery(qry)
            self.ui.tbvKhachHang.resizeColumnsToContents()

    def _tim_dong_model(self, ma_kh):
        """Tìm dòng tương ứng trong model theo MaKH."""
        if not self._table_model or not ma_kh:
            return -1
        for r in range(self._table_model.rowCount()):
            val = self._table_model.data(self._table_model.index(r, 0))
            if str(val) == str(ma_kh):
                return r
        return -1

    def _kh_ton_tai(self, ma_kh):
        """Kiểm tra mã khách hàng đã tồn tại chưa. (True/False)"""
        if not ma_kh:
            return False
        qry_kh = QtSql.QSqlQuery(self.db)
        qry_kh.prepare("SELECT 1 FROM KhachHang WHERE MaKH = :makh")
        qry_kh.bindValue(":makh", ma_kh)
        if not qry_kh.exec():
            return False
        return qry_kh.next()

    def _co_hoadon(self, ma_kh):
        """Kiểm tra nếu có Hóa đơn tham chiếu MaKH (không cho xóa).
        Sử dụng cú pháp tương thích SQL Server (TOP 1).
        Trả về True nếu có ít nhất 1 bản ghi; hoặc nếu truy vấn lỗi -> trả về True (chặn xóa).
        """
        if not ma_kh:
            return False
        qry = QtSql.QSqlQuery(self.db)
        qry.prepare("SELECT TOP 1 1 FROM HoaDon WHERE MaKH = :makh")
        qry.bindValue(":makh", ma_kh)
        if not qry.exec():
            # Nếu truy vấn không thể chạy, chặn xóa để an toàn và hiện lỗi
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi truy vấn", f"Lỗi kiểm tra hóa đơn: {qry.lastError().text()}")
            return True
        return qry.next()

    def _chon_dong_kh(self, current_index, previous_index):
        """Xử lý khi chọn dòng trong bảng KH (dùng view_model)."""
        if self._is_adding:
            return
        row = current_index.row()
        if row < 0 or self._view_model is None or row >= self._view_model.rowCount():
            return
        ma_kh = self._view_model.data(self._view_model.index(row, 0))
        ten_kh = self._view_model.data(self._view_model.index(row, 1))
        sdt = self._view_model.data(self._view_model.index(row, 2))

        self.ui.txtMaKH.setText(str(ma_kh))
        self.ui.txtTenKH.setText(str(ten_kh))
        self.ui.txtSDT.setText(str(sdt))
        self._current_row = row
        self.ui.btnSua.setEnabled(True)
        self.ui.btnXoa.setEnabled(True)

    def _them_kh(self):
        """Thêm Khách hàng: chuẩn bị UI để nhập."""
        self._is_adding = True
        self._is_editing = False
        self._sua_ma_goc = None

        self.ui.txtMaKH.clear()
        self.ui.txtTenKH.clear()
        self.ui.txtSDT.clear()
        self._bat_tat_control(True)

        self.ui.btnThem.setEnabled(False)
        self.ui.btnSua.setEnabled(False)
        self.ui.btnXoa.setEnabled(False)
        self.ui.btnLuu.setEnabled(True)
        self.ui.btnHuy.setEnabled(True)
        self.ui.txtMaKH.setFocus()

    def _sua_kh(self):
        """Sửa Khách hàng: bật UI để chỉnh sửa."""
        row = self._current_row
        if row < 0:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng chọn khách hàng để sửa.")
            return
        self._is_adding = False
        self._is_editing = True
        self._sua_ma_goc = str(self.ui.txtMaKH.text()).strip()
        self._bat_tat_control(True)
        self.ui.txtMaKH.setFocus()

    def _doi_ma_kh_an_toan(self, ma_cu, ma_moi, ten_kh, sdt):
        """Đổi khóa PK MaKH an toàn bằng transaction:
           insert new -> update FK (HoaDon) -> delete old.
           Trả về (ok: bool, message: str)
        """
        if ma_cu == ma_moi:
            return True, ""
        if not ma_cu or not ma_moi:
            return False, "Mã cũ hoặc mã mới không hợp lệ."
        if self._kh_ton_tai(ma_moi):
            return False, f"Mã KH '{ma_moi}' đã tồn tại."

        try:
            if not self.db.transaction():
                return False, "Không thể bắt đầu transaction."

            # 1) Insert new KhachHang
            qry_ins = QtSql.QSqlQuery(self.db)
            qry_ins.prepare("INSERT INTO KhachHang (MaKH, TenKH, SDT) VALUES (:makh, :tenkh, :sdt)")
            qry_ins.bindValue(":makh", ma_moi)
            qry_ins.bindValue(":tenkh", ten_kh)
            qry_ins.bindValue(":sdt", sdt)
            if not qry_ins.exec():
                self.db.rollback()
                return False, f"Lỗi khi chèn KhachHang mới: {qry_ins.lastError().text()}"

            # 2) Update HoaDon FK to new MaKH
            qry_upd_hd = QtSql.QSqlQuery(self.db)
            qry_upd_hd.prepare("UPDATE HoaDon SET MaKH = :new WHERE MaKH = :old")
            qry_upd_hd.bindValue(":new", ma_moi)
            qry_upd_hd.bindValue(":old", ma_cu)
            if not qry_upd_hd.exec():
                self.db.rollback()
                return False, f"Lỗi khi cập nhật HoaDon: {qry_upd_hd.lastError().text()}"

            # 3) Delete old KhachHang
            qry_del = QtSql.QSqlQuery(self.db)
            qry_del.prepare("DELETE FROM KhachHang WHERE MaKH = :old")
            qry_del.bindValue(":old", ma_cu)
            if not qry_del.exec():
                self.db.rollback()
                return False, f"Lỗi khi xóa KhachHang cũ: {qry_del.lastError().text()}"

            if not self.db.commit():
                self.db.rollback()
                return False, "Commit không thành công."
            return True, ""
        except Exception as ex:
            try:
                self.db.rollback()
            except Exception:
                pass
            return False, str(ex)

    def _xoa_kh(self):
        """Xóa Khách hàng nếu không có Hóa đơn tham chiếu."""
        row = self._current_row
        if row < 0:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng chọn Khách hàng để xóa.")
            return
        ma_kh = str(self.ui.txtMaKH.text()).strip()
        if not ma_kh:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Mã khách hàng không hợp lệ.")
            return

        # Nếu có HoaDon tham chiếu => không xóa
        if self._co_hoadon(ma_kh):
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Không thể xóa Khách hàng này vì có hóa đơn tham chiếu.")
            return

        reply = QtWidgets.QMessageBox.question(
            self.parent_window,
            "Xác nhận",
            f"Bạn có chắc muốn xóa khách hàng '{ma_kh}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        try:
            if not self.db.transaction():
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Không thể bắt đầu transaction.")
                return
            qry_del = QtSql.QSqlQuery(self.db)
            qry_del.prepare("DELETE FROM KhachHang WHERE MaKH = :makh")
            qry_del.bindValue(":makh", ma_kh)
            if not qry_del.exec():
                err_text = qry_del.lastError().text()
                # Nếu do FK: thông báo dễ hiểu
                if "REFERENCE constraint" in err_text or "foreign key" in err_text.lower() or "FK_" in err_text:
                    self.db.rollback()
                    QtWidgets.QMessageBox.warning(self.parent_window, "Không thể xóa", "Khách hàng đang có hóa đơn tham chiếu, không thể xóa.")
                    return
                else:
                    self.db.rollback()
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Xóa thất bại: {err_text}")
                    return
            if not self.db.commit():
                self.db.rollback()
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Commit thất bại khi xóa.")
                return
        except Exception as ex:
            try:
                self.db.rollback()
            except Exception:
                pass
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi khi xóa: {ex}")
            return

        QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Xóa khách hàng thành công.")
        # Làm mới UI, làm rỗng các ô nhập
        self._current_row = -1
        self.ui.txtMaKH.clear()
        self.ui.txtTenKH.clear()
        self.ui.txtSDT.clear()
        self._bat_tat_control(False)
        self._lam_moi_models()

    def _luu_kh(self):
        """Lưu Khách hàng (thêm hoặc sửa)."""
        ma_kh = str(self.ui.txtMaKH.text()).strip()
        ten_kh = str(self.ui.txtTenKH.text()).strip()
        sdt = str(self.ui.txtSDT.text()).strip()

        # Validate
        if not ma_kh or not ten_kh or not sdt:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng điền đầy đủ thông tin.")
            return

        # THÊM
        if self._is_adding:
            if self._kh_ton_tai(ma_kh):
                QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", f"Đã tồn tại Mã KH '{ma_kh}'. Vui lòng sử dụng mã khác.")
                self.ui.txtMaKH.setFocus()
                return
            try:
                if not self.db.transaction():
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Không thể bắt đầu transaction.")
                    return
                row = self._table_model.rowCount()
                if not self._table_model.insertRow(row):
                    self.db.rollback()
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Không thể tạo bản ghi mới.")
                    return
                self._table_model.setData(self._table_model.index(row, 0), ma_kh)
                self._table_model.setData(self._table_model.index(row, 1), ten_kh)
                self._table_model.setData(self._table_model.index(row, 2), sdt)
                if not self._table_model.submitAll():
                    self._table_model.revertAll()
                    self.db.rollback()
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Lưu thất bại.")
                    return
                if not self.db.commit():
                    self.db.rollback()
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Commit thất bại khi lưu.")
                    return
                self._table_model.select()
                QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Thêm khách hàng thành công.")
            except Exception as ex:
                try:
                    self.db.rollback()
                except Exception:
                    pass
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi khi thêm: {ex}")
                return

        # SỬA
        elif self._is_editing:
            if self._sua_ma_goc and self._sua_ma_goc != ma_kh:
                ok, msg = self._doi_ma_kh_an_toan(self._sua_ma_goc, ma_kh, ten_kh, sdt)
                if not ok:
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Không thể đổi Mã KH: {msg}")
                    self._lam_moi_models()
                    return
                QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Đổi MaKH thành công.")
            else:
                r = self._tim_dong_model(ma_kh)
                if r < 0:
                    QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Không tìm thấy bản ghi để cập nhật.")
                    return
                try:
                    if not self.db.transaction():
                        QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Không thể bắt đầu transaction.")
                        return
                    self._table_model.setData(self._table_model.index(r, 1), ten_kh)
                    self._table_model.setData(self._table_model.index(r, 2), sdt)
                    if not self._table_model.submitAll():
                        self._table_model.revertAll()
                        self.db.rollback()
                        QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Lưu sửa đổi thất bại.")
                        return
                    if not self.db.commit():
                        self.db.rollback()
                        QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Commit thất bại khi lưu.")
                        return
                    QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Cập nhật khách hàng thành công.")
                except Exception as ex:
                    try:
                        self.db.rollback()
                    except Exception:
                        pass
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi khi cập nhật: {ex}")
                    return

        # Reset trạng thái UI
        self._lam_moi_models()
        self._is_adding = False
        self._is_editing = False
        self._sua_ma_goc = None
        self._bat_tat_control(False)

    def _huy_them_sua_kh(self):
        """Hủy thêm/ sửa Khách hàng"""
        if self._is_adding:
            self.ui.txtMaKH.clear()
            self.ui.txtTenKH.clear()
            self.ui.txtSDT.clear()
        else:
            # revert table model pending changes and restore selected row
            if self._table_model:
                self._table_model.revertAll()
            # reload data and reselect previous row if possible
            self._lam_moi_models()
            if self._current_row >= 0 and self._view_model and self._current_row < self._view_model.rowCount():
                idx = self._view_model.index(self._current_row, 0)
                self._chon_dong_kh(idx, None)
        self._is_adding = False
        self._is_editing = False
        self._sua_ma_goc = None
        self._bat_tat_control(False)