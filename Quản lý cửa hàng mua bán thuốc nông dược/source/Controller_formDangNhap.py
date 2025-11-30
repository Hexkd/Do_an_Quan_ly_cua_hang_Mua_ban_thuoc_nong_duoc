"""
Module để điều khiển form quản lý Đăng nhập
Chứa class Controller_formDangNhap.
"""

from PyQt6 import QtWidgets, QtCore, QtSql

class Controller_formDangNhap:
    """Điều khiển form Đăng nhập"""
    def __init__(self, parent_window, ui_dangnhap, ui_trangchu, db):
        self.parent_window = parent_window
        self.ui = ui_dangnhap
        self.ui_trangchu = ui_trangchu
        self.db = db
        self._setup_ui()
        self._setup_events()

    def _setup_ui(self):
        """Thiết lập giao diện ban đầu"""
        self.ui.txtMatKhau.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

    def _setup_events(self):
        """Kết nối các sự kiện của form Đăng nhập"""
        self.ui.chkHienMK.stateChanged.connect(self._an_hien_mat_khau)
        self.ui.btnDangNhap.clicked.connect(self._dang_nhap)
        self.ui.btnHuy.clicked.connect(self._huy_dang_nhap)
        self.ui.txtMatKhau.returnPressed.connect(self._dang_nhap)

    def _an_hien_mat_khau(self, state):
        """Hiển thị/ẩn mật khẩu"""
        self.ui.txtMatKhau.setFocus()
        if state == QtCore.Qt.CheckState.Checked.value:
            self.ui.txtMatKhau.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        else:
            self.ui.txtMatKhau.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

    def _dang_nhap(self):
        """Xử lý đăng nhập"""
        tai_khoan = self.ui.txtTaiKhoan.text().strip()
        mat_khau = self.ui.txtMatKhau.text().strip()

        if not tai_khoan or not mat_khau:
            QtWidgets.QMessageBox.warning(
                self.parent_window,
                "Lỗi",
                "Vui lòng nhập đầy đủ tài khoản và mật khẩu!"
            )
            return

        # Nếu chưa kết nối CSDL, thông báo lỗi
        if self.db is None or not self.db.isOpen():
            QtWidgets.QMessageBox.critical(
                self.parent_window,
                "Lỗi CSDL",
                "Chưa kết nối được tới cơ sở dữ liệu."
            )
            return

        # Chuẩn bị query truy vấn tài khoản và mật khẩu
        qry_dn = QtSql.QSqlQuery(self.db)
        qry_dn.prepare("SELECT MaTK, Quyen FROM TaiKhoan WHERE MaTK = :tk AND MatKhau = :mk")
        qry_dn.bindValue(":tk", tai_khoan)
        qry_dn.bindValue(":mk", mat_khau)

        #! Thực thi lệnh truy vấn
        # Nếu có kết quả truy vấn, đăng nhập thành công
        if qry_dn.exec() and qry_dn.next():
            # Lưu 'MaTK' và 'Quyen' đã truy vấn
            ma_tk = qry_dn.value(0)
            quyen = qry_dn.value(1)

            # Truy vấn thêm thông tin nhân viên
            qry_nv = QtSql.QSqlQuery(self.db)
            qry_nv.prepare("SELECT MaNV, TenNV, Chucvu FROM NhanVien WHERE MaNV = :manv")
            qry_nv.bindValue(":manv", ma_tk)

            # Nếu truy vấn thông tin nhân viên thành công
            if qry_nv.exec() and qry_nv.next():
                
                # Lưu thông tin Nhân viên
                ma_nv = qry_nv.value(0)
                ten_nv = qry_nv.value(1)
                chuc_vu = qry_nv.value(2)

                # Cập nhật thông tin nhân viên lên form Trang Chủ
                self.ui_trangchu.txtMaNV.setText(str(ma_nv))
                self.ui_trangchu.txtTenNV.setText(str(ten_nv))
                self.ui_trangchu.txtChucVu.setText(str(chuc_vu))
                self.ui_trangchu.txtQuyen.setText(str(quyen))

                # Thông báo đăng nhập thành công
                QtWidgets.QMessageBox.information(
                    self.parent_window,
                    "Thành công",
                    f"Đăng nhập thành công, chào mừng: {ten_nv}"
                )

                # Cập nhật trạng thái menu (sẽ được gọi từ Code_DieuKhien.py)
                self._trang_thai_menu(quyen)
                self.parent_window.close()
            else: # Không có thông tin Nhân viên
                QtWidgets.QMessageBox.critical(
                    self.parent_window,
                    "Lỗi",
                    "Lỗi CSDL: Không tìm thấy thông tin nhân viên chi tiết."
                )
        # Thông báo tài khoản và mật khẩu sai
        elif not qry_dn.lastError().isValid():
            QtWidgets.QMessageBox.critical(
                self.parent_window,
                "Thất bại",
                "Tài khoản hoặc mật khẩu không đúng."
            )
        else:
            QtWidgets.QMessageBox.critical(
                self.parent_window,
                "Lỗi Truy vấn",
                f"Lỗi khi thực thi truy vấn: {qry_dn.lastError().text()}"
            )

    def _trang_thai_menu(self, quyen):
        """Cập nhật trạng thái menu sau khi đăng nhập"""
        self.ui_trangchu.mnuDangNhap.setEnabled(False)
        self.ui_trangchu.mnuDangXuat.setEnabled(True)
        self.ui_trangchu.mnuSanPham.setEnabled(True)
        self.ui_trangchu.mnuKhachHang.setEnabled(True)
        self.ui_trangchu.mnuHoaDon.setEnabled(True)
        if quyen and quyen.lower() == "admin":
            self.ui_trangchu.mnuNhanVien.setEnabled(True)

    def _huy_dang_nhap(self):
        """Hủy đăng nhập"""
        self.parent_window.close()