"""
Module để điều khiển form quản lý Nhân viên
Chứa class Controller_formNhanVien.
"""

from PyQt6 import QtWidgets, QtCore, QtSql

class Controller_formNhanVien:
    """Điều khiển form Nhân Viên"""
    def __init__(self, parent_window, ui_nhanvien, db):
        self.parent_window = parent_window
        self.ui = ui_nhanvien
        self.db = db
        self._table_model = None    # QSqlTableModel (NhanVien) -> để insert/update/delete
        self._view_model = None     # QSqlQueryModel (NhanVien LEFT JOIN TaiKhoan) -> để hiển thị bảng
        self._current_row = -1
        self._is_adding = False
        self._is_editing = False
        self._sua_ma_goc = None
        self._setup_ui()
        self._setup_su_kien()

    def _tao_model_nv_table(self, table_name, headers):
        """Tạo QSqlTableModel cho NhanVien (sử dụng khi cần submit qua model)."""
        if self.db is None or not self.db.isOpen():
            return None
        model = QtSql.QSqlTableModel(parent=self.parent_window, db=self.db)
        model.setTable(table_name)
        model.setEditStrategy(QtSql.QSqlTableModel.EditStrategy.OnManualSubmit)
        model.select()
        for idx, h in enumerate(headers):
            model.setHeaderData(idx, QtCore.Qt.Orientation.Horizontal, h)
        return model

    def _tao_model_nv_view(self):
        """Tạo QSqlQueryModel hiển thị NhanVien và TaiKhoan."""
        if self.db is None or not self.db.isOpen():
            return None
        model = QtSql.QSqlQueryModel(parent=self.parent_window)
        qry = QtSql.QSqlQuery(self.db)
        qry.prepare("""
            SELECT nv.MaNV, nv.TenNV, nv.Chucvu, tk.MaTK, tk.MatKhau, tk.Quyen
            FROM NhanVien nv
            LEFT JOIN TaiKhoan tk ON nv.MaNV = tk.MaTK
            ORDER BY nv.MaNV
        """)
        if not qry.exec():
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi truy vấn: {qry.lastError().text()}")
            return None
        model.setQuery(qry)
        headers = ["Mã NV", "Tên NV", "Chức vụ", "Tài khoản", "Mật khẩu", "Quyền"]
        for idx, h in enumerate(headers):
            model.setHeaderData(idx, QtCore.Qt.Orientation.Horizontal, h)
        return model

    def _setup_ui(self):
        """Thiết lập giao diện ban đầu"""
        # Tạo cả 2 model: table_model (để thao tác), view_model (để hiển thị kết hợp)
        self._table_model = self._tao_model_nv_table("NhanVien", ["Mã NV", "Tên NV", "Chức vụ"])
        self._view_model = self._tao_model_nv_view()
        if self._view_model is None or self._table_model is None:
            return
        self.ui.tbvNhanVien.setModel(self._view_model)  # hiển thị view (có TaiKhoan)
        self.ui.tbvNhanVien.resizeColumnsToContents()
        self.ui.tbvNhanVien.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
        self.ui.tbvNhanVien.setSelectionMode(QtWidgets.QTableView.SelectionMode.SingleSelection)

        # Thiết lập trạng thái control ban đầu
        self._bat_tat_control(False)

    def _setup_su_kien(self):
        """Kết nối các sự kiện"""
        self.ui.tbvNhanVien.selectionModel().currentChanged.connect(self._chon_dong_nv)
        self.ui.btnThem.clicked.connect(self._them_nv)
        self.ui.btnSua.clicked.connect(self._sua_nv)
        self.ui.btnXoa.clicked.connect(self._xoa_nv)
        self.ui.btnLuu.clicked.connect(self._luu_nv)
        self.ui.btnHuy.clicked.connect(self._huy_them_sua_nv)
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
        self.ui.txtMaNV.setReadOnly(not enable)
        self.ui.txtTenNV.setReadOnly(not enable)
        self.ui.txtChucVu.setReadOnly(not enable)
        self.ui.txtMatKhau.setReadOnly(not enable)
        self.ui.rdbNhanVien.setEnabled(enable)
        self.ui.rdbQuanLy.setEnabled(enable)

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
                SELECT nv.MaNV, nv.TenNV, nv.Chucvu, tk.MaTK, tk.MatKhau, tk.Quyen
                FROM NhanVien nv
                LEFT JOIN TaiKhoan tk ON nv.MaNV = tk.MaTK
                ORDER BY nv.MaNV
            """)
            qry.exec()
            self._view_model.setQuery(qry)
            self.ui.tbvNhanVien.resizeColumnsToContents()

    def _nv_ton_tai(self, ma_nv):
        """Kiểm tra mã NV đã tồn tại trong NhanVien không."""
        if not ma_nv:
            return False
        qry = QtSql.QSqlQuery(self.db)
        qry.prepare("SELECT 1 FROM NhanVien WHERE MaNV = :manv")
        qry.bindValue(":manv", ma_nv)
        if not qry.exec():
            return False
        return qry.next()

    def _tk_ton_tai(self, ma_tk):
        """Kiểm tra TaiKhoan(Mã TK) có tồn tại không.
        - |-> True : CÓ tồn tại
        - |-> False: KHÔNG tồn tại
        """
        qry = QtSql.QSqlQuery(self.db)
        qry.prepare("SELECT 1 FROM TaiKhoan WHERE MaTK = :matk")
        qry.bindValue(":matk", ma_tk)
        if not qry.exec():
            return False
        return qry.next()

    def _chon_dong_nv(self, current_index, previous_index):
        """Xử lý khi chọn dòng — sử dụng view_model index (MaNV ở cột 0)."""
        if self._is_adding:
            return
        row = current_index.row()
        if row < 0 or self._view_model is None or row >= self._view_model.rowCount():
            return
        ma_nv = self._view_model.data(self._view_model.index(row, 0))
        ten_nv = self._view_model.data(self._view_model.index(row, 1))
        chucvu = self._view_model.data(self._view_model.index(row, 2))
        matk = self._view_model.data(self._view_model.index(row, 3))
        matkhau = self._view_model.data(self._view_model.index(row, 4))
        quyen = self._view_model.data(self._view_model.index(row, 5))

        self.ui.txtMaNV.setText(str(ma_nv))
        self.ui.txtTenNV.setText(str(ten_nv))
        self.ui.txtMatKhau.setText(str(matkhau))
        self.ui.txtChucVu.setText(str(chucvu))
        if quyen == "admin":
            self.ui.rdbQuanLy.setChecked(True)
            self.ui.rdbNhanVien.setChecked(False)
        else:
            self.ui.rdbQuanLy.setChecked(False)
            self.ui.rdbNhanVien.setChecked(True)

        self._current_row = row

    def _co_hoadon(self, ma_nv):
        """Kiểm tra xem có hóa đơn tham chiếu MaNV không (không cho xóa nếu có)."""
        if not ma_nv:
            return False
        qry = QtSql.QSqlQuery(self.db)
        qry.prepare("SELECT 1 FROM HoaDon WHERE MaNV = :manv LIMIT 1")
        qry.bindValue(":manv", ma_nv)
        if not qry.exec():
            return False
        return qry.next()

    def _them_nv(self):
        """Chuẩn bị để thêm nhân viên."""
        self._is_adding = True
        self._is_editing = False
        self._sua_ma_goc = None

        self.ui.txtMaNV.clear()
        self.ui.txtTenNV.clear()
        self.ui.txtChucVu.clear()
        self.ui.txtMatKhau.clear()
        
        self._bat_tat_control(True)
        self.ui.txtMaNV.setFocus()

    def _sua_nv(self):
        """Bắt đầu sửa nhân viên."""
        row = self._current_row
        if row < 0:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng chọn Nhân viên để sửa.")
            return
        self._is_adding = False
        self._is_editing = True
        self._sua_ma_goc = self.ui.txtMaNV.text().strip()
        self._bat_tat_control(True)
        self.ui.txtMaNV.setFocus()

    def _xoa_nv(self):
        """Xóa Nhân viên (xóa TaiKhoan trước; nếu còn HoaDon thì không cho xóa)."""
        row = self._current_row
        ma_nv = self.ui.txtMaNV.text().strip()
        ma_tk = self._view_model.data(self._view_model.index(row, 3))
        if row < 0:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng chọn nhân viên để xóa.")
            return
        if not ma_nv:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Mã NV không hợp lệ.")
            return
        # Nếu có hóa đơn tham chiếu => không xóa
        if self._co_hoadon(ma_nv):
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Không thể xóa nhân viên này vì đang có hóa đơn tham chiếu.")
            return
        reply = QtWidgets.QMessageBox.question(
            self.parent_window,
            "Xác nhận",
            f"Bạn có chắc muốn xóa nhân viên '{ma_nv}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return


        
        # Xóa trong transaction để đảm bảo xóa đồng bộ
        try:
            #! Bắt đầu transaction
            if not self.db.transaction():
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Không thể bắt đầu transaction.")
                return

            #! Thực hiện xóa TK trước
            qry_del_tk = QtSql.QSqlQuery(self.db)
            qry_del_tk.prepare("DELETE FROM TaiKhoan WHERE MaTK = :matk")
            qry_del_tk.bindValue(":matk", ma_tk)
            if not qry_del_tk.exec(): # Nếu thất bại
                self.db.rollback()
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Xóa tài khoản '{qry_del_tk.lastError().text()}' thất bại.")
                return
            
            #! Thực hiện xóa NhanVien
            qry_del_nv = QtSql.QSqlQuery(self.db)
            qry_del_nv.prepare("DELETE FROM NhanVien WHERE MaNV = :manv")
            qry_del_nv.bindValue(":manv", ma_nv)
            if not qry_del_nv.exec(): # Nếu thất bại
                self.db.rollback()
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Xóa tài khoản '{qry_del_tk.lastError().text()}' thất bại.")
                return
            
            #! Commit transaction
            self.db.commit()
        except Exception as ex:
            self.db.rollback()
            QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi khi xóa: {ex}")
            return

        QtWidgets.QMessageBox.information(self.parent_window, "Thành công", f"Xóa nhân viên '{ma_nv}' thành công.")

        # Reset UI và làm mới bảng
        self._lam_moi_models()
        self._current_row = -1
        self.ui.txtMaNV.clear()
        self.ui.txtTenNV.clear()
        self.ui.txtChucVu.clear()
        self.ui.txtMatKhau.clear()
        self.ui.rdbNhanVien.setChecked(True)
        self.ui.rdbQuanLy.setChecked(False)

    def _doi_ma_nv_an_toan(self, ma_cu, ma_moi, ten_nv, chucvu, matkhau, quyen):
        """Đổi khóa PK MaNV an toàn bằng transaction:
           insert new -> update FK (TaiKhoan/HoaDon) -> delete old.
        Returns (ok: bool, message: str)
        """
        if ma_cu == ma_moi:
            return True, ""
        if not ma_cu or not ma_moi:
            return False, "Mã cũ hoặc Mã mới không hợp lệ."
        if self._nv_ton_tai(ma_moi):
            return False, f"Mã NV '{ma_moi}' đã tồn tại."

        db = self.db
        try:
            if not db.transaction():
                return False, "Không thể bắt đầu transaction."

            # 1. Thêm new NhanVien
            qry_ins = QtSql.QSqlQuery(db)
            qry_ins.prepare("INSERT INTO NhanVien (MaNV, TenNV, Chucvu) VALUES (:manv, :tennv, :cv)")
            qry_ins.bindValue(":manv", ma_moi)
            qry_ins.bindValue(":tennv", ten_nv)
            qry_ins.bindValue(":cv", chucvu)
            if not qry_ins.exec():
                db.rollback()
                return False, f"Lỗi khi thêm NhanVien mới: {qry_ins.lastError().text()}"

            # 2. Cập nhật TaiKhoan (nếu tồn tại)
            if self._tk_ton_tai(ma_cu):
                qry_upd_tk = QtSql.QSqlQuery(db)
                qry_upd_tk.prepare("UPDATE TaiKhoan SET MaTK = :new WHERE MaTK = :old")
                qry_upd_tk.bindValue(":new", ma_moi)
                qry_upd_tk.bindValue(":old", ma_cu)
                if not qry_upd_tk.exec():
                    db.rollback()
                    return False, f"Lỗi khi sửa TaiKhoan mới: {qry_upd_tk.lastError().text()}"

            # 3. Cập nhật HoaDon (nếu tồn tại)
            qry_upd_hd = QtSql.QSqlQuery(db)
            qry_upd_hd.prepare("UPDATE HoaDon SET MaNV = :new WHERE MaNV = :old")
            qry_upd_hd.bindValue(":new", ma_moi)
            qry_upd_hd.bindValue(":old", ma_cu)
            if not qry_upd_hd.exec():
                db.rollback()
                return False, f"Lỗi khi cập nhật HoaDon: {qry_upd_hd.lastError().text()}"

            # 4. Xóa NhanVien cũ
            qry_del_nv = QtSql.QSqlQuery(db)
            qry_del_nv.prepare("DELETE FROM NhanVien WHERE MaNV = :old")
            qry_del_nv.bindValue(":old", ma_cu)
            if not qry_del_nv.exec():
                db.rollback()
                return False, f"Lỗi khi xóa NhanVien cũ: {qry_del_nv.lastError().text()}"

            # 5. Nếu TaiKhoan không tồn tại trên MaNV mới, tạo mới (nếu cần)
            if not self._tk_ton_tai(ma_moi) and matkhau is not None:
                qry_ins_tk = QtSql.QSqlQuery(db)
                qry_ins_tk.prepare("INSERT INTO TaiKhoan (MaTK, MatKhau, Quyen) VALUES (:matk, :mk, :quyen)")
                qry_ins_tk.bindValue(":matk", ma_moi)
                qry_ins_tk.bindValue(":mk", matkhau)
                qry_ins_tk.bindValue(":quyen", quyen)
                if not qry_ins_tk.exec():
                    db.rollback()
                    return False, f"Lỗi khi tạo tài khoản mới: {qry_ins_tk.lastError().text()}"

            if not db.commit():
                db.rollback()
                return False, "Không thể commit transaction."

            return True, ""
        except Exception as ex:
            try:
                db.rollback()
            except Exception:
                pass
            return False, str(ex)

    def _luu_nv(self):
        """Lưu Nhân viên (thêm hoặc sửa) — dùng SQL trực tiếp để tránh lỗi FK."""
        ma_tk = ma_nv = self.ui.txtMaNV.text().strip()
        ten_nv = self.ui.txtTenNV.text().strip()
        chucvu = self.ui.txtChucVu.text().strip()
        matkhau = self.ui.txtMatKhau.text().strip()
        if self.ui.rdbQuanLy.isChecked():
            quyen = "admin"
        else:
            quyen = "nhanvien"

        # Kiểm tra dữ liệu
        if not ma_nv or not ten_nv or not chucvu:
            QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", "Vui lòng nhập đầy đủ thông tin.")
            return

        # THÊM
        if self._is_adding:
            # Thêm: kiểm tra NhanVien có tồn tại hay không
            if self._nv_ton_tai(ma_nv):
                QtWidgets.QMessageBox.warning(self.parent_window, "Lỗi", f"Đã tồn tại Mã NV '{ma_nv}'.")
                self.ui.txtMaNV.setFocus()
                return

            if not self.db.transaction():
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Không thể bắt đầu transaction.")
                return

            #! Thêm Nhân viên
            qry_ins = QtSql.QSqlQuery(self.db)
            qry_ins.prepare("INSERT INTO NhanVien (MaNV, TenNV, Chucvu) VALUES (:manv, :tennv, :cv)")
            qry_ins.bindValue(":manv", ma_nv)
            qry_ins.bindValue(":tennv", ten_nv)
            qry_ins.bindValue(":cv", chucvu)
            if not qry_ins.exec():
                self.db.rollback()
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lỗi khi thêm nhân viên: {qry_ins.lastError().text()}")
                return

            #! Thêm Tài khoản nếu chưa tồn tại hoặc cập nhật nếu tồn tại.
            if not ma_tk:
                return
            if self._tk_ton_tai(ma_tk):
                self._sua_tk(ma_tk, matkhau, quyen)
            qry_ins_tk = QtSql.QSqlQuery(self.db)
            qry_ins_tk.prepare("INSERT INTO TaiKhoan (MaTK, MatKhau, Quyen) VALUES (:matk, :mk, :quyen)")
            qry_ins_tk.bindValue(":matk", ma_tk)
            qry_ins_tk.bindValue(":mk", matkhau)
            qry_ins_tk.bindValue(":quyen", quyen)
            if not qry_ins_tk.exec():
                QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", "Không thể tạo tài khoản cho nhân viên mới.")
                self.db.rollback()
                return
            
            #! Commit transaction
            self.db.commit()
            QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Thêm nhân viên thành công.")

        # SỬA
        elif self._is_editing:
            # Sửa: nếu đổi mã gốc, dùng rename transaction; nếu không, update đơn giản
            if self._sua_ma_goc and self._sua_ma_goc != ma_nv:
                ok, msg = self._doi_ma_nv_an_toan(self._sua_ma_goc, ma_nv, ten_nv, chucvu, matkhau, quyen)
                if not ok:
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Không thể đổi Mã NV: {msg}")
                    self._lam_moi_models()
                    return
            else:
                # update NhanVien (theo MaNV)
                qry_upd = QtSql.QSqlQuery(self.db)
                qry_upd.prepare("UPDATE NhanVien SET TenNV = :tennv, Chucvu = :cv WHERE MaNV = :manv")
                qry_upd.bindValue(":manv", ma_nv)
                qry_upd.bindValue(":tennv", ten_nv)
                qry_upd.bindValue(":cv", chucvu)
                if not qry_upd.exec():
                    QtWidgets.QMessageBox.critical(self.parent_window, "Lỗi", f"Lưu sửa đổi thất bại: {qry_upd.lastError().text()}")
                    return

                # cập nhật TaiKhoan mật khẩu/quyền nếu có
                if matkhau or quyen:
                    set_parts = []
                    set_parts.append("MatKhau = :mk")
                    set_parts.append("Quyen = :quyen")
                    if not set_parts:
                        return True
                    qry_str = f"UPDATE TaiKhoan SET {', '.join(set_parts)} WHERE MaTK = :matk"
                    qry_upd_tk = QtSql.QSqlQuery(self.db)
                    qry_upd_tk.prepare(qry_str)
                    if matkhau is not None:
                        qry_upd_tk.bindValue(":mk", matkhau)
                    if quyen is not None:
                        qry_upd_tk.bindValue(":quyen", quyen)
                    qry_upd_tk.bindValue(":matk", ma_tk)

                    if not qry_upd_tk.exec(): # Thất bại
                        QtWidgets.QMessageBox.warning(self.parent_window, "Cảnh báo", "Cập nhật tài khoản thất bại (kiểm tra chi tiết).")

            QtWidgets.QMessageBox.information(self.parent_window, "Thành công", "Cập nhật nhân viên thành công.")

        # Reset trạng thái UI
        self._is_adding = False
        self._is_editing = False
        self._sua_ma_goc = None
        self._bat_tat_control(False)
        # Làm mới hiển thị
        self._lam_moi_models()

    def _huy_them_sua_nv(self):
        """Hủy thao tác Thêm/Sửa."""
        if self._is_adding:
            self.ui.txtMaNV.clear()
            self.ui.txtTenNV.clear()
            self.ui.txtChucVu.clear()
            self.ui.txtMatKhau.clear()
        else:
            # restore selected row if still exist
            self._lam_moi_models()
            if self._current_row >= 0 and self._view_model and self._current_row < self._view_model.rowCount():
                idx = self._view_model.index(self._current_row, 0)
                self._chon_dong_nv(idx, None)
        self._is_adding = False
        self._is_editing = False
        self._sua_ma_goc = None
        self._bat_tat_control(False)