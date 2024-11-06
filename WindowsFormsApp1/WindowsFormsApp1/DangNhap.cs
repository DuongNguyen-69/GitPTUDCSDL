using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WindowsFormsApp1
{
    public class DangNhap
    {
        public string TaiKhoan { get; set; }
        public string MatKhau { get; set; }
        public string HoTen { get; set; }
        public string Quyen { get; set; }

        public DangNhap() { }
        public DangNhap(String taiKhoan, string matKhau, string hoTen, string quyen)
        {
            TaiKhoan = taiKhoan;
            MatKhau = matKhau;
            HoTen = hoTen;
            Quyen = quyen; 
            
        }
    }
}
