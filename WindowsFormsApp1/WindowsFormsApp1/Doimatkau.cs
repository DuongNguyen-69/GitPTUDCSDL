using System;
using System.Data.SqlClient;
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
    public partial class Doimatkau : Form
    {
        private string  connectionString = @"Data Source=ADMIN-PC;Initial Catalog=baitaplon;Integrated Security=True";
        public Doimatkau()
        {
            InitializeComponent();
        }

        private void label4_Click(object sender, EventArgs e)
        {

        }

        private void btn_xacnhan_Click(object sender, EventArgs e)
        {
            // Lấy dữ liệu người dùng
            string TenDangNhap = txt_TenDN.Text;
            string MatKhauCu = txt_mkcu.Text;
            string MatKhauMoi = txt_mkmoi.Text;
            string XacNhanMatKhau = txt_xacnhan.Text;
            // Check rỗng
            if (string.IsNullOrEmpty(TenDangNhap) ||
                string.IsNullOrEmpty(MatKhauCu)  ||
                string.IsNullOrEmpty(MatKhauMoi) ||
                string.IsNullOrEmpty(XacNhanMatKhau))
            {
                MessageBox.Show("Bạn đã điền thiếu thông tin !", "Thông báo");
                return;
            }
            // Check mật khẩu mới và xác nhận có trùng không
            if (MatKhauMoi != XacNhanMatKhau)
            {
                MessageBox.Show("Mật khẩu của bạn không khớp !!!", "Thông báo");
                return;
            }
            try
            {
                // Kết nối tới SQL Server
                using (SqlConnection conn = new SqlConnection(connectionString))
                {
                    conn.Open();
                    // Check mật khẩu cũ có đúng không
                    string queryCheck = "SELECT COUNT(*) FROM DangNhap WHERE TenDangNhap =@TenDangNhap AND MatKhau = @MatKhauCu  ";
                    using (SqlCommand cmd = new SqlCommand(queryCheck, conn))
                    {
                        cmd.Parameters.AddWithValue("@TenDangNhap", TenDangNhap);
                        cmd.Parameters.AddWithValue("@MatKhauCu", MatKhauCu);

                        int count = (int)cmd.ExecuteScalar();

                        // Check sai tk và mk
                        if(count == 0)
                        {
                            MessageBox.Show("Tên đăng nhập hoặc mật khẩu sai!", "Thông báo");
                            return;
                        }

                    }
                    string queryUpdate = "UPDATE DangNhap SET MatKhau = @matKhauMoi WHERE TenDangNhap = @tenDangNhap";
                    using (SqlCommand cmd = new SqlCommand(queryUpdate, conn))
                    {
                        cmd.Parameters.AddWithValue("@TenDangNhap", TenDangNhap);
                        cmd.Parameters.AddWithValue("@MatKhauMoi", MatKhauMoi);

                        cmd.ExecuteNonQuery(); // thực thi đổi mật khẩu

                        MessageBox.Show("Đổi mật khẩu thành công", "Thông báo");
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Lỗi: {ex.Message}", "Thông báo");
            }

        }

        private void btn_huy_Click(object sender, EventArgs e)
        {
            var kq = MessageBox.Show("Bạn có muốn thoát", "Thông báo", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            if (kq == DialogResult.Yes)
            {
                this.Close();
            }
        }
    }
}
