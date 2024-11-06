using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    public partial class Form1 : Form
    {

        public Form1()
        {
            InitializeComponent();
        }

       
        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void textBox2_TextChanged(object sender, EventArgs e)
        {

        }

        private void btnDangNhap_Click(object sender, EventArgs e)
        {
            string tenDangNhap = txtTenDangNhap.Text;
            String matKhau = txtMatKhau.Text;
            bool isFound = false;
            foreach(var dn in DataProvider.DangNhaps)
            {
                if(dn.TaiKhoan == tenDangNhap && dn.MatKhau == matKhau)
                {
                    isFound = true;
                    break;
                   
                
                }
              
            }
            if (isFound)
            {
                MessageBox.Show("Đăng nhập thành công");
                MainFrm f = new MainFrm();
                f.ShowDialog();
            }
            else
            {
                MessageBox.Show(" sai tên tài khoản hoặc mật khẩu");
            }
        }

        private void btnThoat_Click(object sender, EventArgs e)
        {
            Dispose();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            DataProvider.GetAllDangNhap();
        }

        private void txtTenDangNhap_TextChanged(object sender, EventArgs e)
        {

        }
    }
}
