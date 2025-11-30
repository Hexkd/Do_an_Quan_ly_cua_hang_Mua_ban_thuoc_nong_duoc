"""
Module để điều khiển form quản lý Hóa đơn
Chứa class Controller_formHoaDon.
"""

from PyQt6 import QtWidgets, QtCore, QtSql, QtGui

class Controller_formHoaDon:
    """Điều khiển form Hóa Đơn"""
    def __init__(self, parent_window, ui_hoadon, db):
        self.parent_window = parent_window
        self.ui = ui_hoadon
        self.db = db
        self._model = None
        self._current_row = -1
        self._is_adding = False
        self._is_editing = False
        self._setup_ui()
        self._setup_su_kien()

    def _setup_ui(self):
        """Thiết lập giao diện ban đầu"""
        self._model = self._tao_model_hd()
        if self._model is None:
            return
        self.ui.tbvHoaDon.setModel(self._model)
        self.ui.tbvHoaDon.resizeColumnsToContents()
        self.ui.tbvHoaDon.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.ui.tbvHoaDon.setSelectionMode(QtWidgets.QTableView.SelectionMode.SingleSelection)

        self._bat_tat_control(False)

    def _setup_su_kien(self):
        """Kết nối các sự kiện"""
        self.ui.tbvHoaDon.selectionModel().currentChanged.connect(self._chon_dong_hd)
        self.ui.btnThem.clicked.connect(self._them_hd)
        self.ui.btnSua.clicked.connect(self._sua_hd)
        self.ui.btnXoa.clicked.connect(self._xoa_hd)
        self.ui.btnLuu.clicked.connect(self._luu_hd)
        self.ui.btnHuy.clicked.connect(self._huy_them_sua_hd)
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
        self.ui.txtMaHD.setReadOnly(not enable)
        self.ui.txtMaNV.setReadOnly(not enable)
        self.ui.txtMaSP.setReadOnly(not enable)
        self.ui.txtMaKH.setReadOnly(not enable)
        self.ui.txtSoLuong.setReadOnly(not enable)

        self.ui.btnThem.setEnabled(not enable)
        self.ui.btnSua.setEnabled(not enable)
        self.ui.btnXoa.setEnabled(not enable)
        self.ui.btnLuu.setEnabled(enable)
        self.ui.btnHuy.setEnabled(enable)

    def _tao_model_hd(self):
        """Tạo QSqlQueryModel cho bảng HóaĐơn"""
        if self.db is None or not self.db.isOpen():
            return None
        model = QtSql.QSqlQueryModel(parent=self.parent_window)
        query = QtSql.QSqlQuery(self.db)
        query.prepare("""
            SELECT hd.MaHD, hd.NgayLap, sp.TenSP, hd.MaNV, hd.MaKH, hd.MaSP, hd.SoLuong, hd.ThanhTien
            FROM HoaDon hd
            LEFT JOIN SanPham sp ON hd.MaSP = sp.MaSP
        """)
        if not query.exec():
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi truy vấn: {query.lastError().text()}")
            return None
        model.setQuery(query)
        headers = ["Mã HĐ", "Ngày lập", "Tên SP", "Mã NV", "Mã KH", "Mã SP", "Số lượng", "Thành tiền"]
        for idx, h in enumerate(headers):
            model.setHeaderData(idx, QtCore.Qt.Orientation.Horizontal, h)
        return model

    def _lam_moi_model(self):
        """Làm mới lại model"""
        query = QtSql.QSqlQuery(self.db)
        query.prepare("""
            SELECT hd.MaHD, hd.NgayLap, sp.TenSP, hd.MaNV, hd.MaKH, hd.MaSP, hd.SoLuong, hd.ThanhTien
            FROM HoaDon hd
            LEFT JOIN SanPham sp ON hd.MaSP = sp.MaSP
        """)
        query.exec()
        self._model.setQuery(query)

    def _chon_dong_hd(self, current_index, previous_index):
        """Xử lý khi chọn dòng"""
        if self._is_adding:
            return
        row = current_index.row()
        if row < 0 or row >= self._model.rowCount():
            return
        mahd = self._model.data(self._model.index(row, 0))
        ngay = self._model.data(self._model.index(row, 1))
        manv = self._model.data(self._model.index(row, 3))
        makh = self._model.data(self._model.index(row, 4))
        masp = self._model.data(self._model.index(row, 5))
        sl = self._model.data(self._model.index(row, 6))
        tt = self._model.data(self._model.index(row, 7))
        self.ui.txtMaHD.setText(str(mahd))
        try:
            self.ui.dtpNgayLap.setDate(QtCore.QDate.fromString(str(ngay), 'yyyy-MM-dd'))
        except Exception:
            pass
        self.ui.txtMaNV.setText(str(manv))
        self.ui.txtMaKH.setText(str(makh))
        self.ui.txtMaSP.setText(str(masp))
        self.ui.txtSoLuong.setText(str(sl))
        self.ui.txtThanhTien.setText(str(tt))
        self._current_row = row
        self.ui.btnSua.setEnabled(True)
        self.ui.btnXoa.setEnabled(True)

    def _them_hd(self):
        """Thêm Hóa đơn"""
        self._is_adding = True
        self._is_editing = False
        self.ui.txtMaHD.clear()
        self.ui.txtMaNV.clear()
        self.ui.txtMaKH.clear()
        self.ui.txtMaSP.clear()
        self.ui.txtSoLuong.clear()
        self.ui.txtThanhTien.clear()
        self._bat_tat_control(True)
        self.ui.txtMaHD.setFocus()

    def _sua_hd(self):
        """Sửa Hóa đơn"""
        row = self._current_row
        if row < 0:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng chọn hóa đơn để sửa.")
            return
        self._is_adding = False
        self._is_editing = True
        self._bat_tat_control(True)
        self.ui.txtMaHD.setFocus()

    def _xoa_hd(self):
        """Xóa Hóa đơn"""
        row = self._current_row
        if row < 0:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng chọn hóa đơn để xóa.")
            return
        reply = QtWidgets.QMessageBox.question(
            self.parent_window,
            "Xác nhận",
            "Bạn có chắc muốn xóa?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        mahd = self.ui.txtMaHD.text().strip()
        qry_delete = QtSql.QSqlQuery(self.db)
        qry_delete.prepare("DELETE FROM HoaDon WHERE MaHD = :mahd")
        qry_delete.bindValue(":mahd", mahd)
        if not qry_delete.exec():
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Xóa thất bại.")
            return
        self._lam_moi_model()
        self.ui.txtMaHD.clear()
        self.ui.txtMaNV.clear()
        self.ui.txtMaKH.clear()
        self.ui.txtMaSP.clear()
        self.ui.txtSoLuong.clear()
        self.ui.txtThanhTien.clear()
        self._current_row = -1

    def _luu_hd(self):
        """Lưu Hóa đơn"""
        mahd = self.ui.txtMaHD.text().strip()
        ngay = self.ui.dtpNgayLap.date().toString('yyyy-MM-dd')
        manv = self.ui.txtMaNV.text().strip()
        makh = self.ui.txtMaKH.text().strip()
        masp = self.ui.txtMaSP.text().strip()
        sl = self.ui.txtSoLuong.text().strip()

        if not mahd or not ngay or not manv or not makh or not masp or not sl:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return

        try:
            qty = float(sl)
            if qty <= 0:
                QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Số lượng phải lớn hơn 0.")
                return
        except Exception:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Số lượng không hợp lệ.")
            return

        # Lấy giá từ SanPham
        qry_price = QtSql.QSqlQuery(self.db)
        qry_price.prepare("SELECT Gia, SoLuong FROM SanPham WHERE MaSP = :masp")
        qry_price.bindValue(":masp", masp)
        if not (qry_price.exec() and qry_price.next()):
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Sản phẩm '{masp}' không tồn tại.")
            return
        
        try:
            price_num = float(qry_price.value(0))
            stock_num = float(qry_price.value(1))
        except Exception:
            price_num = 0.0
            stock_num = 0.0

        if qty > stock_num:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Số lượng vượt quá tồn kho.")
            return

        thanh_tien = price_num * qty

        if self._is_adding:
            qry_insert = QtSql.QSqlQuery(self.db)
            qry_insert.prepare("""
                INSERT INTO HoaDon (MaHD, NgayLap, MaNV, MaKH, MaSP, SoLuong, ThanhTien)
                VALUES (:mahd, :ngay, :mnv, :mkh, :msp, :sl, :tt)
            """)
            qry_insert.bindValue(":mahd", mahd)
            qry_insert.bindValue(":ngay", ngay)
            qry_insert.bindValue(":mnv", manv)
            qry_insert.bindValue(":mkh", makh)
            qry_insert.bindValue(":msp", masp)
            qry_insert.bindValue(":sl", sl)
            qry_insert.bindValue(":tt", thanh_tien)
            if not qry_insert.exec():
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lưu thất bại: {qry_insert.lastError().text()}")
                return
            QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Thêm hóa đơn thành công.")
        else:
            qry_update = QtSql.QSqlQuery(self.db)
            qry_update.prepare("""
                UPDATE HoaDon SET NgayLap = :ngay, MaNV = :mnv, MaKH = :mkh, MaSP = :msp, SoLuong = :sl, ThanhTien = :tt
                WHERE MaHD = :mahd
            """)
            qry_update.bindValue(":ngay", ngay)
            qry_update.bindValue(":mnv", manv)
            qry_update.bindValue(":mkh", makh)
            qry_update.bindValue(":msp", masp)
            qry_update.bindValue(":sl", sl)
            qry_update.bindValue(":tt", thanh_tien)
            qry_update.bindValue(":mahd", mahd)
            if not qry_update.exec():
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lưu sửa đổi thất bại: {qry_update.lastError().text()}")
                return
            QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Cập nhật hóa đơn thành công.")

        self._lam_moi_model()
        self._is_adding = False
        self._is_editing = False
        self._bat_tat_control(False)

    def _huy_them_sua_hd(self):
        """Hủy"""
        if self._is_adding:
            self.ui.txtMaHD.clear()
            self.ui.txtMaNV.clear()
            self.ui.txtMaKH.clear()
            self.ui.txtMaSP.clear()
            self.ui.txtSoLuong.clear()
            self.ui.txtThanhTien.clear()
        else:
            row = self._current_row
            if row >= 0 and row < self._model.rowCount():
                self.ui.txtMaHD.setText(str(self._model.data(self._model.index(row, 0))))
                try:
                    self.ui.dtpNgayLap.setDate(QtCore.QDate.fromString(str(self._model.data(self._model.index(row, 1))), 'yyyy-MM-dd'))
                except Exception:
                    pass
                self.ui.txtMaNV.setText(str(self._model.data(self._model.index(row, 3))))
                self.ui.txtMaKH.setText(str(self._model.data(self._model.index(row, 4))))
                self.ui.txtMaSP.setText(str(self._model.data(self._model.index(row, 5))))
                self.ui.txtSoLuong.setText(str(self._model.data(self._model.index(row, 6))))
                self.ui.txtThanhTien.setText(str(self._model.data(self._model.index(row, 7))))
        self._is_adding = False
        self._is_editing = False
        self._bat_tat_control(True)