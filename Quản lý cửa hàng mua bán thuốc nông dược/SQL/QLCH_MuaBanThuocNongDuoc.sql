USE master
GO
-- Xóa CSDL cũ nếu tồn tại
IF EXISTS (SELECT name FROM sys.databases WHERE name = N'QLCH_MuaBanThuocNongDuoc')
BEGIN
    ALTER DATABASE [QLCH_MuaBanThuocNongDuoc] SET SINGLE_USER WITH ROLLBACK IMMEDIATE
    DROP DATABASE [QLCH_MuaBanThuocNongDuoc]
END
GO

--------------------------------------------------------------------------------------------
-- Tạo CSDL tên [QLCH_MuaBanThuocNongDuoc]
--------------------------------------------------------------------------------------------
CREATE DATABASE [QLCH_MuaBanThuocNongDuoc]
GO
USE [QLCH_MuaBanThuocNongDuoc]
GO

--------------------------------------------------------------------------------------------
-- Tạo các bảng
--------------------------------------------------------------------------------------------

-- Bảng NhanVien
CREATE TABLE NhanVien (
    MaNV NVARCHAR(6) UNIQUE NOT NULL,
    TenNV NVARCHAR(50) NOT NULL,
    Chucvu NVARCHAR(20) NOT NULL,
)
GO

-- Bảng KhachHang
CREATE TABLE KhachHang (
    MaKH NVARCHAR(6) UNIQUE NOT NULL,
    TenKH NVARCHAR(100) NOT NULL,
    SDT VARCHAR(10) NOT NULL,
)
GO

-- Bảng SanPham
CREATE TABLE SanPham (
    MaSP NVARCHAR(6) UNIQUE NOT NULL,
    TenSP NVARCHAR(100) NOT NULL,
    Gia INT NOT NULL DEFAULT 0,
    SoLuong INT NOT NULL DEFAULT 0,
)
GO

-- Bảng TaiKhoan
CREATE TABLE TaiKhoan (
    MaTK NVARCHAR(6) NOT NULL,
    MatKhau VARCHAR(50) NOT NULL DEFAULT '123',
    Quyen NVARCHAR(10) NOT NULL DEFAULT N'Nhanvien',
)
GO

-- Bảng HoaDon
CREATE TABLE HoaDon (
    MaHD NVARCHAR(6) UNIQUE NOT NULL,
    NgayLap DATE NOT NULL DEFAULT '2001-01-01',
    MaNV NVARCHAR(6) NOT NULL,
    MaKH NVARCHAR(6) NOT NULL,
    MaSP NVARCHAR(6) NOT NULL,
    SoLuong INT NOT NULL,
    ThanhTien INT NOT NULL,
)
GO

--------------------------------------------------------------------------------------------
-- Các khóa chính
--------------------------------------------------------------------------------------------
ALTER TABLE NhanVien
ADD CONSTRAINT PK_NHANVIEN PRIMARY KEY (MaNV)
GO

ALTER TABLE KhachHang
ADD CONSTRAINT PK_KHACHHANG PRIMARY KEY (MaKH)
GO

ALTER TABLE SanPham
ADD CONSTRAINT PK_SANPHAM PRIMARY KEY (MaSP)
GO

ALTER TABLE TaiKhoan
ADD CONSTRAINT PK_TAIKHOAN PRIMARY KEY (MaTK)
GO

ALTER TABLE HoaDon
ADD CONSTRAINT PK_HOADON PRIMARY KEY (MaHD)
GO
--------------------------------------------------------------------------------------------
-- Các khóa ngoại
--------------------------------------------------------------------------------------------
-- Khóa ngoại đã hợp lệ về kiểu dữ liệu
ALTER TABLE TaiKhoan
ADD CONSTRAINT FK_TAIKHOAN_NHANVIEN FOREIGN KEY (MaTK) REFERENCES NhanVien(MaNV)
GO

ALTER TABLE HoaDon
ADD CONSTRAINT FK_HOADON_SANPHAM FOREIGN KEY (MaSP) REFERENCES SanPham(MaSP)
ALTER TABLE HoaDon
ADD CONSTRAINT FK_HOADON_NHANVIEN FOREIGN KEY (MaNV) REFERENCES NhanVien(MaNV)
ALTER TABLE HoaDon
ADD CONSTRAINT FK_HOADON_KHACHHANG FOREIGN KEY (MaKH) REFERENCES KhachHang(MaKH)
GO

--------------------------------------------------------------------------------------------
-- Thêm dữ liệu vào các cột
--------------------------------------------------------------------------------------------
-- Bảng NhanVien
INSERT INTO NhanVien (MaNV, TenNV, Chucvu) VALUES
    (N'nv001', N'Nguyễn Văn A', N'Tổng quản lý'),
    (N'nv002', N'Trần Thị B', N'Kế toán'),
    (N'nv003', N'Lê Văn C', N'Bán hàng'),
    (N'nv004', N'Phạm Thị D', N'Bán hàng'),
    (N'nv005', N'Hoàng Minh E', N'Thủ kho'),
    (N'nv006', N'Đỗ Xuân F', N'Quản lý chi nhánh')
GO

-- Bảng TaiKhoan
INSERT INTO TaiKhoan (MaTK, MatKhau, Quyen) VALUES
    (N'nv001', '001', N'admin'),
    (N'nv002', '002', N'nhanvien'),
    (N'nv003', '003', N'nhanvien'),
    (N'nv004', '004', N'nhanvien'),
    (N'nv005', '005', N'nhanvien'),
    (N'nv006', '006', N'admin')
GO

-- Bảng KhachHang
INSERT INTO KhachHang (MaKH, TenKH, SDT) VALUES
    (N'kh001', N'Phạm Quang Dũng', '0901112222'),
    (N'kh002', N'Hoàng Mai Lan', '0913334444'),
    (N'kh003', N'Công Ty Thuận Thiên', '0285556666'),
    (N'kh004', N'Trang trại Long An', '0977889900'),
    (N'kh005', N'Nguyễn Văn Hưng', '0861234567'),
    (N'kh006', N'Vựa nông sản Sáu Tèo', '0945551212'),
    (N'kh007', N'Lâm Văn Kiệt', '0933778899')
GO

-- Bảng SanPham
INSERT INTO SanPham (MaSP, TenSP, Gia, SoLuong) VALUES
    (N'sp001', N'Thuốc trừ sâu Anvil 5SC', 120000, 500),
    (N'sp002', N'Phân bón NPK 30-10-10', 45000, 300),
    (N'sp003', N'Thuốc diệt cỏ Gramoxone', 200000, 200),
    (N'sp004', N'Thuốc trừ bệnh Validacin', 80000, 250),
    (N'sp005', N'Giống lúa OM5451', 35000, 800),
    (N'sp006', N'Phân bón hữu cơ T99', 75000, 400),
    (N'sp007', N'Chất điều hòa sinh trưởng GA3', 150000, 150),
    (N'sp008', N'Thuốc trừ rầy Bassa 50EC', 95000, 350),
    (N'sp009', N'Hạt giống rau muống', 12000, 1000),
    (N'sp010', N'Thuốc diệt ốc Snail Killer', 60000, 600)
GO

--------------------------------------------------------------------------------------------
-- Bảng HoaDon (Dữ liệu đã sửa lỗi khóa ngoại MaKH)
--------------------------------------------------------------------------------------------
-- Khách hàng: kh001 - kh007
-- Nhân viên bán hàng: nv003, nv004, nv001 (Quản lý có thể bán hàng)

INSERT INTO HoaDon (MaHD, MaSP, MaNV, MaKH, NgayLap, SoLuong, ThanhTien) VALUES
    -- Hóa đơn 1: Khách hàng kh001 mua sp001 (120000 * 30 = 3600000)
    (N'hd001', N'sp001', N'nv003', N'kh001', '2025-10-15', 30, 3600000),
    -- Hóa đơn 2: Khách hàng kh002 mua sp004 (80000 * 10 = 800000)
    (N'hd002', N'sp004', N'nv004', N'kh002', '2025-10-15', 10, 800000),
    -- Hóa đơn 3: Khách hàng kh003 mua sp003 (200000 * 50 = 10000000)
    (N'hd003', N'sp003', N'nv003', N'kh003', '2025-10-16', 50, 10000000),
    -- Hóa đơn 4: Khách hàng kh004 mua sp005 (35000 * 100 = 3500000)
    (N'hd004', N'sp005', N'nv004', N'kh004', '2025-10-16', 100, 3500000),
    -- Hóa đơn 5: Khách hàng kh005 mua sp006 (75000 * 5 = 375000)
    (N'hd005', N'sp006', N'nv003', N'kh005', '2025-10-17', 5, 375000),
    -- Hóa đơn 6: Khách hàng kh006 mua sp007 (150000 * 20 = 3000000)
    (N'hd006', N'sp007', N'nv004', N'kh006', '2025-10-18', 20, 3000000),
    -- Hóa đơn 7: Khách hàng kh004 quay lại mua sp008 (95000 * 25 = 2375000)
    (N'hd007', N'sp008', N'nv004', N'kh004', '2025-10-19', 25, 2375000),
    -- Hóa đơn 8: Khách hàng kh007 mua sp009 (12000 * 2 = 24000)
    (N'hd008', N'sp009', N'nv003', N'kh007', '2025-10-20', 2, 24000),
    -- Hóa đơn 9: Khách hàng kh003 mua sp010 (60000 * 40 = 2400000)
    (N'hd009', N'sp010', N'nv003', N'kh003', '2025-10-21', 40, 2400000),
    -- Hóa đơn 10: Khách hàng kh001 mua sp002 (45000 * 5 = 225000)
    (N'hd010', N'sp002', N'nv001', N'kh001', '2025-10-22', 5, 225000)
GO