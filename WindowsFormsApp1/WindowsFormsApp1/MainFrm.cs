using System;
using System.Data;
using System.Data.SqlClient;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    public partial class MainFrm : Form
    {
        private string connectionString = "Data Source=MSI\SQLEXPRESS;Initial Catalog=baitaplon;User ID=sa;Password=12345";

        public MainFrm()
        {
            InitializeComponent();
        }

        private DataTable getData(string query)
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
                    MessageBox.Show($"Có lỗi xảy ra: {ex.Message}");
                    return null;
                }
            }
        }

        private bool run(string query)
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
                    MessageBox.Show($"Có lỗi xảy ra: {ex.Message}");
                    return false;
                }
            }
        }

        private void MainFrm_Load(object sender, EventArgs e)
        {
            getData("SELECT * FROM Khoa");
            getData("SELECT * FROM SinhVien");
            getData("SELECT * FROM MonHoc");
            getData("SELECT * FROM KetQua");
            getData("SELECT * FROM DangNhap");
        }

        private void label3_Click(object sender, EventArgs e) { }
        private void label2_Click(object sender, EventArgs e) { }
        private void label4_Click(object sender, EventArgs e) { }
        private void txtNoiDung_TextChanged(object sender, EventArgs e) { }
    }
}
