﻿create database baitaplon
use baitaplon

create table DangNhap(
	TenDangNhap varchar(50) primary key,
	Hoten nvarchar(100),
	MatKhau varchar(50),
	Quyen nvarchar(50),
);

create table Khoa (
	MaKhoa varchar(50) primary key,
	TenKhoa nvarchar(100)
)

create table SinhVien(
	MaSV int primary key,
	HoTen nvarchar(100) , 
	NgaySinh datetime,
	GioiTinh nvarchar(10),
	DiaChi nvarchar(100),
	DienThoai varchar(20) unique,
	MaKhoa varchar(50) references Khoa (MaKhoa)
)

create table MonHoc(
	MaMH varchar(50) primary key, 
	TenMH nvarchar(100),
	SoTin int
)

create table KetQua(
	MaSV int,
	MaMH varchar(50) references MonHoc(MaMH),
	Diem decimal,
	primary key (MaSV, MaMH)
)

insert into DangNhap values 
('lebao', N'Lê Quốc Bảo', '1111', 'Admin'),
('duong', N'Nguyễn Văn Dương', '2222', 'Admin'),
('chinh', N'Phạm Phúc Chính', '3333', 'Admin'),
('dat', N'Nguyễn Tiến Đạt', '4444', 'Admin'),
('thang', N'Trịnh Quang Thắng', '5555', 'Admin');

insert into Khoa values
('CNTT', N'Công nghệ thông tin'),
('KT', N'Kinh tế');


insert into SinhVien values
(123, N'Nguyễn Văn A', '2004-3-17', N'Nam', 'HP', '0898419728', 'CNTT'),
(321, N'Lê Quốc B', '2003-9-21', N'Nam', 'HP', '0898419764', 'CNTT'),
(112, N'Phạm Phúc C', '2003-5-8', N'Nam', 'HP', '0898419149', 'CNTT'),
(132, N'Trịnh Trần Phương T', '2004-10-9', N'Nữ', 'HP', '0898419687', 'CNTT'),
(345, N'Nguyễn Tiến E', '2004-4-16', N'Nam', 'HP', '0898419964', 'CNTT');


insert into MonHoc values
('17301', N'Kỹ thuật vi xử lý', 3),
('17526', N'Hệ điều hành mạng', 3),
('17234', N'Trí tuệ nhân tạo', 3),
('17314', N'Phát triên ứng dụng mã nguồn mở', 3),
('17434', N'Phát triên ứng dụng & CSDL', 3);

insert into KetQua values
(123,'17301',8),
(123,'17526',7),
(123,'17234',8),
(123,'17314',9),
(123,'17434',7);