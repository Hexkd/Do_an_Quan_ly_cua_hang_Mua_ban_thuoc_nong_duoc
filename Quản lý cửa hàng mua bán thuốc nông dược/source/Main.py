"""Module chính khởi chạy phần mềm QLCH_MuaBanThuocNongDuoc."""

import sys
# Sử dụng công cụ PyQt để xây dựng UI form cho phần mềm QLCH_MuaBanThuocNongDuoc
from PyQt6 import QtWidgets, QtSql
# Import các UI đã xây dựng bằng ứng dụng Qt Designer
from formTrangChu import Ui_formTrangChu
from formDangNhap import Ui_formDangNhap
from formSanPham import Ui_formSanPham
from formKhachHang import Ui_formKhachHang
from formHoaDon import Ui_formHoaDon
from formNhanVien import Ui_formNhanVien
# Import các Module điều khiển form trực tiếp từ thư mục chứa file này
from Controller_formDangNhap import Controller_formDangNhap
from Controller_formSanPham import Controller_formSanPham
from Controller_formKhachHang import Controller_formKhachHang
from Controller_formHoaDon import Controller_formHoaDon
from Controller_formNhanVien import Controller_formNhanVien


app = QtWidgets.QApplication(sys.argv)
db = None

connection_string = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=.;"
    "Database=QLCH_MuaBanThuocNongDuoc;"
    "TRUSTED_CONNECTION=yes;"
)

def ket_noi_db():
    global db
    db = QtSql.QSqlDatabase.addDatabase("QODBC")
    db.setDatabaseName(connection_string)
    if not db.open():
        error = db.lastError().text()
        QtWidgets.QMessageBox.critical(
            None, "Lỗi Kết nối CSDL",
            f"Không thể kết nối tới cơ sở dữ liệu: {error}"
        )
        return False
    return True

def ensure_db_connected(parent_window=None):
    global db
    if db is not None and hasattr(db, 'isOpen') and db.isOpen():
        return True
    ok = ket_noi_db()
    if not ok and parent_window is not None:
        QtWidgets.QMessageBox.critical(
            parent_window, "Lỗi CSDL",
            "Không thể kết nối tới cơ sở dữ liệu."
        )
    return ok

def main():
    global db
    TrangChu_window = QtWidgets.QMainWindow()
    ui_TrangChu = Ui_formTrangChu()
    ui_TrangChu.setupUi(TrangChu_window)
    ui_TrangChu._dialogs = []

    try:
        ket_noi_db()
    except Exception:
        pass

    def mnudangnhap(checked=False):
        DangNhap_win = QtWidgets.QMainWindow(parent=TrangChu_window)
        ui_DangNhap = Ui_formDangNhap()
        ui_DangNhap.setupUi(DangNhap_win)
        
        ensure_db_connected(DangNhap_win)
        controller = Controller_formDangNhap(parent_window=DangNhap_win, ui_dangnhap=ui_DangNhap, ui_trangchu=ui_TrangChu, db=db)
        
        ui_TrangChu._dialogs.append((DangNhap_win, ui_DangNhap, controller))
        DangNhap_win.show()

    def mnudangxuat(checked=False):
        ui_TrangChu.txtMaNV.setText("n/a")
        ui_TrangChu.txtTenNV.setText("n/a")
        ui_TrangChu.txtChucVu.setText("n/a")
        ui_TrangChu.txtQuyen.setText("n/a")
        menu_logged_in(status=False)

    def mnusanpham(checked=False):
        SanPham_win = QtWidgets.QMainWindow(parent=TrangChu_window)
        ui_SanPham = Ui_formSanPham()
        ui_SanPham.setupUi(SanPham_win)
        
        ensure_db_connected(SanPham_win)
        controller = Controller_formSanPham(SanPham_win, ui_SanPham, db)
        
        ui_TrangChu._dialogs.append((SanPham_win, ui_SanPham, controller))
        SanPham_win.show()

    def mnukhachhang(checked=False):
        KhachHang_win = QtWidgets.QMainWindow(parent=TrangChu_window)
        ui_KhachHang = Ui_formKhachHang()
        ui_KhachHang.setupUi(KhachHang_win)
        
        ensure_db_connected(KhachHang_win)
        controller = Controller_formKhachHang(KhachHang_win, ui_KhachHang, db)
        
        ui_TrangChu._dialogs.append((KhachHang_win, ui_KhachHang, controller))
        KhachHang_win.show()

    def mnunhanvien(checked=False):
        NhanVien_win = QtWidgets.QMainWindow(parent=TrangChu_window)
        ui_NhanVien = Ui_formNhanVien()
        ui_NhanVien.setupUi(NhanVien_win)
        
        ensure_db_connected(NhanVien_win)
        controller = Controller_formNhanVien(NhanVien_win, ui_NhanVien, db)
        
        ui_TrangChu._dialogs.append((NhanVien_win, ui_NhanVien, controller))
        NhanVien_win.show()

    def mnuhoadon(checked=False):
        HoaDon_win = QtWidgets.QMainWindow(parent=TrangChu_window)
        ui_HoaDon = Ui_formHoaDon()
        ui_HoaDon.setupUi(HoaDon_win)
        
        ensure_db_connected(HoaDon_win)
        controller = Controller_formHoaDon(HoaDon_win, ui_HoaDon, db)
        
        ui_TrangChu._dialogs.append((HoaDon_win, ui_HoaDon, controller))
        HoaDon_win.show()

    def menu_logged_in(status=False):
        ui_TrangChu.mnuDangNhap.setEnabled(not status)
        ui_TrangChu.mnuDangXuat.setEnabled(status)
        ui_TrangChu.mnuSanPham.setEnabled(status)
        ui_TrangChu.mnuKhachHang.setEnabled(status)
        ui_TrangChu.mnuNhanVien.setEnabled(False)
        ui_TrangChu.mnuHoaDon.setEnabled(status)

    ui_TrangChu.mnuDangNhap.triggered.connect(mnudangnhap)
    ui_TrangChu.mnuDangXuat.triggered.connect(mnudangxuat)
    ui_TrangChu.mnuThoat.triggered.connect(TrangChu_window.close)
    ui_TrangChu.mnuSanPham.triggered.connect(mnusanpham)
    ui_TrangChu.mnuKhachHang.triggered.connect(mnukhachhang)
    ui_TrangChu.mnuNhanVien.triggered.connect(mnunhanvien)
    ui_TrangChu.mnuHoaDon.triggered.connect(mnuhoadon)

    TrangChu_window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()