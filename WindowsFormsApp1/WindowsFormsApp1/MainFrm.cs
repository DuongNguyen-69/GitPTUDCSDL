using System;
using System.Data;
using System.Data.SqlClient;
using System.Windows.Forms;
using System.Collections.Generic;

namespace WindowsFormsApp1
{
    public partial class MainFrm : Form
    {
        private string connectionString = "Data Source=ADMIN-PC\\SQLEXPRESS;Initial Catalog=baitaplon;Integrated Security=True";
        private DataTable dt = new DataTable();

        public MainFrm()
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
                    MessageBox.Show($"Có lỗi xảy ra: {ex.Message}");
                    return false;
                }
            }
        }

        private void MainFrm_Load(object sender, EventArgs e)
        {
            GetData("SELECT * FROM Khoa");
            GetData("SELECT * FROM SinhVien");
            GetData("SELECT * FROM MonHoc");
            GetData("SELECT * FROM KetQua");
            GetData("SELECT * FROM DangNhap");
            dtgvMonHoc.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill; 
        }

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

            string query = "INSERT INTO MonHoc (MaMH, TenMH, SoTiet) VALUES (@MaMH, @TenMH, @SoTiet)";

            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    using (var cmd = new SqlCommand(query, conn))
                    {
                        
                        cmd.Parameters.AddWithValue("@MaMH", maMH);
                        cmd.Parameters.AddWithValue("@TenMH", tenMh);
                        cmd.Parameters.AddWithValue("@SoTiet", soTiet);

                        int kq = cmd.ExecuteNonQuery();  

                        if (kq > 0)
                        {
                            MessageBox.Show("Thêm môn học thành công");
                            LoadTableMonHoc();
                            UnenableControl(new List<Control> { txtMaMH, TxtTenMH, txtSoTiet, btnLuu });
                            ResetText(new List<Control> { txtMaMH, TxtTenMH, txtSoTiet });
                        }
                        else
                        {
                            MessageBox.Show("Không thể thêm môn học, vui lòng xem lại");
                        }
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Có lỗi xảy ra: {ex.Message}");
                }
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
            dt = GetData(query);  
            dtgvMonHoc.DataSource = dt;
        }

        private void dtgvMonHoc_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {
            if (e.RowIndex >= 0) 
            {
                
                txtMaMH.Text = dtgvMonHoc.Rows[e.RowIndex].Cells[dtgvMonHoc.Columns["MaMH"].Index].Value.ToString();
                TxtTenMH.Text = dtgvMonHoc.Rows[e.RowIndex].Cells[dtgvMonHoc.Columns["TenMH"].Index].Value.ToString();
                txtSoTiet.Text = dtgvMonHoc.Rows[e.RowIndex].Cells[dtgvMonHoc.Columns["SoTin"].Index].Value.ToString(); 

                EnableControls(new List<Control> { txtSoTiet, txtMaMH, TxtTenMH, btnXoa, btnSua });
            }
        }

        private void comboMaMH_Click(object sender, EventArgs e)
        {
            LoadComboMaMH();

        }
        private void LoadComboMaMH()
        {
            string query = "SELECT MaMH, TenMH from MonHoc";
            comboMaMH.DataSource = DataProvider.LoadCSDL(query);
            comboMaMH.DisplayMember = "TenMH";
            comboMaMH.ValueMember = "MaMH";

        }

        private void btnTimMonHocTheoMa_Click(object sender, EventArgs e)
        {
            string maMH = (string)comboMaMH.SelectedValue;
            string query = $"Select * from MonHoc where maMH ='{maMH}'";
            dt.Clear();
            dt = DataProvider.LoadCSDL(query);
            dtgvMonHoc.DataSource = dt;

        }
    }
    }

