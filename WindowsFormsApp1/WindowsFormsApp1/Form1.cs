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
        private int wrongAttempts = 0;

        public Form1()
        {
            InitializeComponent();
        }

        private void btnDangNhap_Click(object sender, EventArgs e)
        {
            string tenDangNhap = txtTenDangNhap.Text;
            string matKhau = txtMatKhau.Text;

            if (string.IsNullOrWhiteSpace(tenDangNhap))
            {
                MessageBox.Show("Chưa nhập tên tài khoản.");
                return; 
            }

            if (string.IsNullOrWhiteSpace(matKhau))
            {
                MessageBox.Show("Chưa nhập mật khẩu.");
                return; 
            }

            bool isFound = false;
            foreach (var dn in DataProvider.DangNhaps)
            {
                if (dn.TaiKhoan == tenDangNhap && dn.MatKhau == matKhau)
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
                this.Close();
            }
            else
            {
                wrongAttempts++;
                int remainingAttempts = 5 - wrongAttempts;

                if (remainingAttempts > 0)
                {
                    MessageBox.Show($"Tài khoản hoặc mật khẩu sai. Bạn còn {remainingAttempts} lần sai.");
                }
                else
                {
                    MessageBox.Show("Bạn đã nhập sai 5 lần. Đóng chương trình.");
                    this.Close();
                }
            }
        }

        private void btnThoat_Click(object sender, EventArgs e)
        {
            this.Close(); 
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            DataProvider.GetAllDangNhap();
        }

        private void btnHienmk_Click(object sender, EventArgs e)
        {
           
            if (txtMatKhau.UseSystemPasswordChar)
            {
                txtMatKhau.UseSystemPasswordChar = false;
                btnHienmk.Text = "Ẩn mật khẩu";
            }
            else
            {
                txtMatKhau.UseSystemPasswordChar = true;
                btnHienmk.Text = "Hiện mật khẩu";
            }
        }
    }
}