using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Data.SqlClient;
using System.Data.Common;
using System.Configuration;
namespace WindowsFormsApp1
{
    public partial class CapNhatSinhVien : Form
    {
        private string connectionString = ConfigurationManager.ConnectionStrings["MyConnectionString"].ConnectionString;
        public CapNhatSinhVien()
        {
            InitializeComponent();
        }

        private DataTable GetData(string query)
        {
            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    var da = new SqlDataAdapter(query, conn);
                    var dt = new DataTable();
                    da.Fill(dt);
                    dgvCapNhatSV.DataSource = dt;
                    return dt;
                }
                catch(Exception ex)
                {
                    MessageBox.Show(ex.Message);return null;
                }
            }
        }

        private bool RunQuery(string query)
        {
            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    var com = new SqlCommand(query, conn);
                    com.ExecuteNonQuery();
                    return true;
                }
                catch(Exception ex)
                {
                    MessageBox.Show(ex.Message);
                    return false;
                }
            }
        }
        

        private void CapNhatSinhVien_Load(object sender, EventArgs e)
        {
            GetData("select * from SinhVien");
        }

        private void btnThem_Click(object sender, EventArgs e)
        {
            string query = @"INSERT INTO SinhVien (MaSV, HoTen, NgaySinh, GioiTinh, DiaChi, DienThoai,TenKhoa) 
                     VALUES (@MaSV, @HoTen, @NgaySinh, @GioiTinh, @DiaChi, @DienThoai,@TenKhoa)";
            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    var com = new SqlCommand(query, conn);
                    com.Parameters.AddWithValue("@MaSV", txtMSV.Text.Trim());
                    com.Parameters.AddWithValue("@HoTen", txtHoTen.Text.Trim());
                    com.Parameters.AddWithValue("@NgaySinh", dtpNS.Value.ToString()); // sửa định dang ngày"yyyy/MM/dd"
                    com.Parameters.AddWithValue("@GioiTinh", cbbGioiTinh.Text.Trim());
                    com.Parameters.AddWithValue("@DiaChi", txtDC.Text.Trim());
                    com.Parameters.AddWithValue("@DienThoai", txtDT.Text.Trim());
                    com.Parameters.AddWithValue("@TenKhoa", txtTenKhoa.Text.Trim());
                    com.ExecuteNonQuery();
                    MessageBox.Show("Thêm thành công");
                    GetData("select * from SinhVien");
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
        }


        private void btnSua_Click(object sender, EventArgs e)
        {
            /*
            string query = @"update SinhVien set HoTen = @HoTen,
                                                NgaySinh = @NgaySinh,
                                                GioiTinh = @GioiTinh,
                                                DiaChi = @DiaChi,
                                                DienThoai = @DienThoai 
                                             where
                                                MaSV = @MaSV;";
            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    var com = new SqlCommand(query, conn);
                    com.Parameters.AddWithValue("@MaSV", txtMSV.Text.Trim());
                    com.Parameters.AddWithValue("@HoTen", txtHoTen.Text.Trim());
                    com.Parameters.AddWithValue("@NgaySinh", dtpNS.Value.ToString());
                    com.Parameters.AddWithValue("@GioiTinh", cbbGioiTinh.Text.Trim());
                    com.Parameters.AddWithValue("@DiaChi", txtDC.Text.Trim());
                    com.Parameters.AddWithValue("@DienThoai", txtDT.Text.Trim());
                    com.ExecuteNonQuery();
                    MessageBox.Show("Sửa thành công");
                    GetData("select * from SinhVien");
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
            */
            
            string query = @"update SinhVien set HoTen = @HoTen,
                                                NgaySinh = @NgaySinh,
                                                GioiTinh = @GioiTinh,
                                                DiaChi = @DiaChi,
                                                DienThoai = @DienThoai,
                                                TenKhoa = @TenKhoa
                                             where
                                                MaSV = @MaSV;
";
            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    var com = new SqlCommand(query, conn);
                    com.Parameters.AddWithValue("@MaSV", txtMSV.Text.Trim());
                    com.Parameters.AddWithValue("@HoTen", txtHoTen.Text.Trim());
                    com.Parameters.AddWithValue("@NgaySinh", dtpNS.Value.ToString());
                    com.Parameters.AddWithValue("@GioiTinh", cbbGioiTinh.Text.Trim());
                    com.Parameters.AddWithValue("@DiaChi", txtDC.Text.Trim());
                    com.Parameters.AddWithValue("@DienThoai", txtDT.Text.Trim());
                    com.Parameters.AddWithValue("@TenKhoa", txtTenKhoa.Text.Trim());
                    com.ExecuteNonQuery();
                    MessageBox.Show("Sửa thành công");
                    GetData("select * from SinhVien");
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
            
        }

        private void btnXoa_Click(object sender, EventArgs e)
        {
            string query = @"delete from SinhVien where MaSV = @MaSV";
            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    var com = new SqlCommand(query, conn);
                    com.Parameters.AddWithValue("@MaSV", txtMSV.Text.Trim());
                    com.ExecuteNonQuery();
                    MessageBox.Show("Xoá thành công");
                    GetData("select * from SinhVien");
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
        }

        private void dgvCapNhatSV_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            txtMSV.Text = dgvCapNhatSV.Rows[e.RowIndex].Cells[0].Value.ToString();
            txtHoTen.Text = dgvCapNhatSV.Rows[e.RowIndex].Cells[1].Value.ToString();
            dtpNS.Text = dgvCapNhatSV.Rows[e.RowIndex].Cells[2].Value.ToString(); //moi sua bang thg em theo dung dinh dang
            cbbGioiTinh.Text = dgvCapNhatSV.Rows[e.RowIndex].Cells[3].Value.ToString();
            txtDC.Text = dgvCapNhatSV.Rows[e.RowIndex].Cells[4].Value.ToString();
            txtDT.Text = dgvCapNhatSV.Rows[e.RowIndex].Cells[5].Value.ToString();
            txtTenKhoa.Text = dgvCapNhatSV.Rows[e.RowIndex].Cells[6].Value.ToString();
        }
    }
}
