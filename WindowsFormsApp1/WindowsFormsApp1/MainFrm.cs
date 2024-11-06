using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Data.SqlClient;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace WindowsFormsApp1
{
    public partial class MainFrm : Form
    {

        private string connectionString = @"Data Source=MSI\SQLEXPRESS;Initial Catalog=baitaplon;User ID=sa;Password=12345";
        SqlConnection conn = null;
        public MainFrm()
        {
            InitializeComponent();
        }

        private DataTable getData(String query)
        {
            using (var conn = new SqlConnection(connectionString))
            {
                conn.Open();
                var com = new SqlCommand(query, conn);
                com.ExecuteNonQuery();
                var dt = new DataTable();
                var da = SqlDataAdapter(com);
                da.Fill(dt);
                conn.Close();
                dtgvMonHoc.DataSource = dt;
                return dt;
            }
        }

      
    

        private object SqlDataAdapter(SqlCommand com)
        {
            throw new NotImplementedException();
        }

        private bool run(String query)
        {
            using (var conn = new SqlConnection(connectionString))
            {
                conn.Open();
                var com = new SqlCommand(query, conn);
                com.ExecuteNonQuery();
                conn.Close();
                return true;
            }
        }

        private void label3_Click(object sender, EventArgs e)
        {

        }

        private void label2_Click(object sender, EventArgs e)
        {

        }

        private void label4_Click(object sender, EventArgs e)
        {

        }

        private void txtNoiDung_TextChanged(object sender, EventArgs e)
        {

        }

        private void MainFrm_Load(object sender, EventArgs e)
        {
            getData("select*from Khoa");
            getData("select*from SinhVien");
            getData("select*from MonHoc");
            getData("select*from KetQua");
            getData("select*from DangNhap");
        }
    }
}
