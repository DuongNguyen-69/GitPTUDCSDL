using System;
using System.Data;
using System.Data.SqlClient;
using System.Windows.Forms;
using System.Collections.Generic;


namespace WindowsFormsApp1
{
    public partial class MainFrm : Form
    {
        private string connectionString = "Data Source=ADMIN-PC;Initial Catalog=baitaplon;Integrated Security=True";
        private DataTable dt = new DataTable();
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

        private void btnThem_Click(object sender, EventArgs e)
        {
            EnableControls(new List<Control> { txtMaMH, TxtTenMH, txtSoTiet, btnLuu });
            ResetText(new List<Control> { txtMaMH, TxtTenMH, txtSoTiet });
            txtMaMH.Focus();
        }
        private void EnableControls(List<Control> controls)
        {
            foreach (var control in controls)
            {
                control.Enabled = true;
            }
        }
        private void UnenableControl(List<Control> controls)
        {
            foreach (Control control in controls)
            {
                control.Enabled = false;
            }
        }
        private void ResetText(List<Control> controls)
        {
            foreach (Control control in controls)
            {
                control.Text = "";
            }

        }

        private void btnLuu_Click(object sender, EventArgs e)
        {
            string maMH = txtMaMH.Text;
            string tenMh = TxtTenMH.Text;
            string soTiet = txtSoTiet.Text;

            string query = $"INSERT INTO MonHoc VALUES ('{maMH}', N'{tenMh}', {soTiet})";

            int kq = DataProvider.ThaoTacCSDL(query);
            if (kq>0)
            {
                MessageBox.Show("Thêm môn học thành công");
                LoadTableMonHoc();
                UnenableControl(new List<Control> { txtMaMH, TxtTenMH, txtSoTiet,btnLuu });
                ResetText(new List<Control> { txtMaMH, TxtTenMH, txtSoTiet });
            }
            else
            {
                MessageBox.Show("Không thể thêm môn học, vui lòng xem lại");
            }
        }

        private void btnHienThiTatCa_Click(object sender, EventArgs e)
        {
            LoadTableMonHoc();
        }
        private void LoadTableMonHoc()
        {
            string query = "SELECT * FROM MonHoc";
            dt.Clear();
            dt = DataProvider.LoadCSDL(query);
            dtgvMonHoc.DataSource = dt;
        }
        

    }
}
