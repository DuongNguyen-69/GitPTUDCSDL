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
    public partial class SuaMonHoc : Form
    {
        private string connectionString = ConfigurationManager.ConnectionStrings["MyConnectionString"].ConnectionString;
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
                    dtgvMonHoc.DataSource = dt;
                    return dt;
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message); return null;
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
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                    return false;
                }
            }
        }
        public SuaMonHoc()
        {
            InitializeComponent();
        }

        private void SuaMonHoc_Load(object sender, EventArgs e)
        {
            GetData("select * from MonHoc");
        }

        private void btnSuatimkiem_Click(object sender, EventArgs e)
        {
            string query = "UPDATE MonHoc SET TenMH = @TenMH, SoTin = @SoTin WHERE MaMH = @MaMH";

            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    var com = new SqlCommand(query, conn);
                    com.Parameters.AddWithValue("@MaMH", txtMaMH.Text.Trim());
                    com.Parameters.AddWithValue("@TenMH", TxtTenMH.Text.Trim());             
                    com.Parameters.AddWithValue("@SoTin", txtSoTin.Text.Trim());
                    com.ExecuteNonQuery();
                    MessageBox.Show("Sửa thành công");
                    GetData("SELECT * FROM MonHoc"); 
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Đã xảy ra lỗi: " + ex.Message); 
                }
            }
        }

        private void btnXoasuatimkiem_Click(object sender, EventArgs e)
        {
            string query = @"delete from MonHoc where MaMH = @MaMH";
            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    var com = new SqlCommand(query, conn);
                    com.Parameters.AddWithValue("@MaSV", txtMaMH.Text.Trim());
                    com.ExecuteNonQuery();
                    MessageBox.Show("Xoá thành công");
                    GetData("select * from MonHoc");
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
        }

        private void btnThoattimkiem_Click(object sender, EventArgs e)
        {
            DialogResult rs = MessageBox.Show("Bạn có muốn thoát", "Thông báo", MessageBoxButtons.OKCancel);
            if (rs == DialogResult.OK)
                this.Close();
        }

        private void dtgvMonHoc_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }
    }
}
