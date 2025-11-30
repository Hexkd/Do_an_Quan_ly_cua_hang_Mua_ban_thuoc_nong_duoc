import tkinter as tk
from tkinter.ttk import *
from tkinter import messagebox as MessageBox
import pyodbc # Thư viện kết nối CSDL

# ==============================================================================
# 1. Khai báo Cấu hình CSDL
# ==============================================================================

# VUI LÒNG THAY THẾ CÁC GIÁ TRỊ PLACEHOLDER BẰNG THÔNG TIN KẾT NỐI THỰC TẾ CỦA BẠN
# SỬ DỤNG WINDOWS AUTHENTICATION: Cần đảm bảo tài khoản Windows đang chạy ứng dụng
# đã được cấp quyền truy cập vào SQL Server và Database này.
CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"   # Đảm bảo driver này đã được cài đặt
    "SERVER=(localhost);"                       # Ví dụ:.\SQLEXPRESS hoặc tên Server đầy đủ
    "DATABASE=QLCH_BanThuocNongDuoc;"           # Tên CSDL đã tạo
    "Trusted_Connection=yes;"                   # Kích hoạt Windows Authentication
)

# Khai báo các biến toàn cục
quyen_han = ""        # Biến lưu quyền hạn người dùng sau khi đăng nhập
is_logged_in = False  # Trạng thái đăng nhập

# ==============================================================================
# 2. Lớp Kết nối Cơ sở Dữ liệu (DBConnector)
# ==============================================================================

class DBConnector:
    """Quản lý kết nối, thực thi truy vấn và quản lý tài nguyên (cursor, connection)
    để đảm bảo tính ổn định và bảo mật (ngăn SQL Injection bằng tham số hóa).
    """
    def __init__(self):
        self.connection_string = CONNECTION_STRING

    def execute_query(self, sql_query, params=None, fetch_all=False, commit=False):
        cnxn = None
        cursor = None
        data = None
        try:
            # Thiết lập kết nối sử dụng Windows Authentication
            cnxn = pyodbc.connect(self.connection_string)
            cursor = cnxn.cursor()

            # Thực thi truy vấn (Sử dụng tham số hóa) [1]
            if params:
                cursor.execute(sql_query, params)
            else:
                cursor.execute(sql_query)

            # Xử lý kết quả (SELECT)
            if sql_query.strip().upper().startswith("SELECT"):
                if fetch_all:
                    data = cursor.fetchall()
                else:
                    data = cursor.fetchone()
            
            # Xử lý giao dịch (INSERT, UPDATE, DELETE)
            if commit:
                cnxn.commit()
                data = cursor.rowcount # Trả về số dòng bị ảnh hưởng
            
            return data

        except pyodbc.Error as ex:
            # Lấy thông tin lỗi chi tiết để debug [2]
            print(f"Lỗi pyodbc xảy ra: {ex}")
            # Hoàn tác giao dịch nếu có lỗi DML [3]
            if cnxn:
                cnxn.rollback()
            return None 

        finally:
            # Đảm bảo đóng tài nguyên ngay cả khi có lỗi [4, 3]
            if cursor:
                cursor.close()
            if cnxn:
                cnxn.close()


# ==============================================================================
# 3. Form Trang chủ (FormTrangChu)
# ==============================================================================
class FormTrangChu:
    def __init__(self, master): # Khởi tạo form trang chủ
        self.login_form = None
        self.master = master
        master.title("Trang chủ - Quản lý Cửa hàng bán Thuốc nông dược")
        master.geometry("600x400")

        # Tạo thanh menu
        menubar = tk.Menu(master)
        master.config(menu=menubar)
        # Các menu cha
        menu_hethong = tk.Menu(menubar, tearoff=0)
        menu_quanly = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hệ thống", menu=menu_hethong)
        menubar.add_cascade(label="Quản lý", menu=menu_quanly)
        
        # Các mục trong menu Hệ thống
        self.mnuDang_nhap_index = menu_hethong.index("end")
        menu_hethong.add_command(label="Đăng nhập...", command=self.mnuDang_nhap, state="normal")
        self.mnuDang_xuat_index = menu_hethong.index("end")
        menu_hethong.add_command(label="Đăng xuất", command=self.mnuDang_xuat, state="disabled")
        menu_hethong.add_separator()
        menu_hethong.add_command(label="Thoát", command=self.mnuThoat)
        
        # Các mục trong menu Quản lý
        menu_quanly.add_command(label="Sản phẩm...", command=self.mnuSanPham, state="disabled")
        self.mnuSanPham_index = menu_quanly.index("end") - 1 
        
        menu_quanly.add_command(label="Khách hàng...", command=self.mnuKhachHang, state="disabled")
        self.mnuKhachHang_index = menu_quanly.index("end") - 1 
        
        menu_quanly.add_separator()
        
        self.mnuNhanVien_index = menu_quanly.index("end")
        menu_quanly.add_command(label="Nhân viên...", command=self.mnuNhanVien, state="disabled")

        self.menu_quanly = menu_quanly
        self.menu_hethong = menu_hethong 

        # Nội dung chính của form trang chủ
        self.lblWelcome = tk.Label(master, text="Chào mừng đến với\nPhần mềm Quản lý cửa hàng Thuốc nông dược!", font=("Arial", 16))
        self.lblWelcome.pack(pady=20)

    def mnuDang_nhap(self): # Mở form đăng nhập
        if self.login_form is None or not tk.Toplevel.winfo_exists(self.login_form.master):
            self.login_form = FormDangNhap(self.master, callback=self.on_login_success)
        else:
            self.login_form.master.lift()
            self.login_form.master.focus_force()

    def on_login_success(self): # Callback khi đăng nhập thành công
        global is_logged_in, quyen_han
        is_logged_in = True
        
        # Cấu hình lại menu Hệ thống
        self.menu_hethong.entryconfig(self.mnuDang_nhap_index, state="disabled")
        self.menu_hethong.entryconfig(self.mnuDang_xuat_index, state="normal")
        
        # Bật menu Quản lý chung
        self.menu_quanly.entryconfig(self.mnuSanPham_index, state="normal")
        self.menu_quanly.entryconfig(self.mnuKhachHang_index, state="normal")
        
        # Cấu hình lại menu Quản lý dựa trên quyền hạn
        if quyen_han.lower() == "admin":
            self.menu_quanly.entryconfig(self.mnuNhanVien_index, state="normal")

    def mnuDang_xuat(self): # Xử lý lệnh đăng xuất
        global is_logged_in, quyen_han
        is_logged_in = False
        quyen_han = "" # Xóa quyền hạn
        
        # Cấu hình lại menu Hệ thống
        self.menu_hethong.entryconfig(self.mnuDang_nhap_index, state="normal")
        self.menu_hethong.entryconfig(self.mnuDang_xuat_index, state="disabled")
        
        # Tắt tất cả menu quản lý
        self.menu_quanly.entryconfig(self.mnuSanPham_index, state="disabled")
        self.menu_quanly.entryconfig(self.mnuKhachHang_index, state="disabled")
        self.menu_quanly.entryconfig(self.mnuNhanVien_index, state="disabled")
        MessageBox.showinfo("Đăng xuất", "Bạn đã đăng xuất thành công!")
        
    def mnuSanPham(self): # Xử lý mục Sản phẩm
        # ===================================
        # TODO: Mở form Sản phẩm
        # ===================================
        pass
        
    def mnuKhachHang(self): # Xử lý mục Khách hàng
        # ===================================
        # TODO: Mở form Khách hàng
        # ===================================
        pass
        
    def mnuNhanVien(self): # Xử lý mục Nhân viên
        # ===================================
        # TODO: Mở form Nhân viên
        # ===================================
        pass

    def mnuThoat(self): # Xử lý lệnh thoát
        self.master.quit()

# ==============================================================================
# 4. Form đăng nhập (FormDangNhap)
# ==============================================================================
class FormDangNhap:
    def __init__(self, master, callback=None):
        self.master = tk.Toplevel(master)
        self.master.title("Đăng Nhập")
        self.master.geometry("300x180")
        self.callback = callback
        self.db_connector = DBConnector() # Khởi tạo đối tượng kết nối

        # Cấu hình Grid
        self.master.columnconfigure(0, weight=1)
        self.master.columnconfigure(1, weight=3)
        
        # Label cho Tài khoản
        self.lblMaTK = tk.Label(self.master, text="Tài khoản:")
        self.lblMaTK.grid(row=0, column=0, padx=5, pady=10)
        # Entry cho Tài khoản
        self.txtMaTK = tk.Entry(self.master)
        self.txtMaTK.grid(row=0, column=1, padx=5, pady=10)

        # Label cho Mật khẩu
        self.lblMatKhau = tk.Label(self.master, text="Mật khẩu:")
        self.lblMatKhau.grid(row=1, column=0, padx=5, pady=10)
        # Entry cho Mật khẩu
        self.txtMatKhau = tk.Entry(self.master, show="*")
        self.txtMatKhau.grid(row=1, column=1, padx=5, pady=10)

        # Checkbox Hiện mật khẩu
        self.chkHienMatKhau = tk.IntVar()
        self.chkHienMatKhauBtn = tk.Checkbutton(self.master, text="Hiện mật khẩu", variable=self.chkHienMatKhau, command=self.HienMatKhau)
        self.chkHienMatKhauBtn.grid(row=2, column=1, padx=0, pady=0)

        # Khung chứa nút
        frame_buttons = tk.Frame(self.master)
        frame_buttons.grid(row=3, column=0, columnspan=2, pady=10)

        # Button Hủy
        self.btnHuy = tk.Button(frame_buttons, text="Hủy", command=self.btnhuy, width=10)
        self.btnHuy.pack(side=tk.LEFT, padx=10)
        # Button Đăng nhập
        self.btnDangNhap = tk.Button(frame_buttons, text="Đăng Nhập", command=self.btndangnhap, width=10)
        self.btnDangNhap.pack(side=tk.LEFT, padx=10)

    def HienMatKhau(self): # Hiện/Ẩn mật khẩu (mặc định là ẩn)
        if self.chkHienMatKhau.get():
            self.txtMatKhau.config(show="")
        else:
            self.txtMatKhau.config(show="*")

    def btnhuy(self): # Xử lý Button hủy
        self.master.destroy()

    def btndangnhap(self): # Xử lý Button đăng nhập
        global quyen_han
        
        ma_tk_input = self.txtMaTK.get()
        mat_khau_input = self.txtMatKhau.get()

        if not ma_tk_input or not mat_khau_input:
            MessageBox.showwarning("Lỗi", "Vui lòng nhập đầy đủ Tài khoản và Mật khẩu!")
            return

        # ----------------------------------------------------------------------
        # Logic Xác thực Người dùng (Application Authentication)
        # ----------------------------------------------------------------------
        
        # Sử dụng truy vấn tham số hóa để ngăn chặn SQL Injection [1]
        sql_query = f"SELECT Quyen FROM TaiKhoan WHERE MaTK={0} AND MatKhau ={1}", ma_tk_input, mat_khau_input
        
        params = (ma_tk_input, mat_khau_input)
        
        # Thực thi truy vấn - Kết nối CSDL bằng tài khoản Windows
        result = self.db_connector.execute_query(sql_query, params=params, fetch_all=False)
        
        if result:
            # Đăng nhập thành công
            # result là một tuple (Quyen,)
            quyen_han_db = result 
            quyen_han = str(quyen_han_db).strip() # Chuyển thành chuỗi và cắt bỏ khoảng trắng
            
            MessageBox.showinfo("Đăng nhập thành công!", f"Quyền hạn: {quyen_han}")
            
            if self.callback:
                self.callback()
                
            self.master.destroy()
        else:
            # Đăng nhập thất bại (Tài khoản không tồn tại hoặc Mật khẩu sai)
            MessageBox.showerror("Lỗi", "Sai mã tài khoản hoặc mật khẩu!")
        
        # ----------------------------------------------------------------------

# ==============================================================================
# 5. Chạy ứng dụng
# ==============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = FormTrangChu(root)
    root.mainloop()