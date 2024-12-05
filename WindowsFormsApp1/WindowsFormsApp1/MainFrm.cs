using System;
using System.Data;
using System.Data.SqlClient;
using System.Windows.Forms;
using System.Collections.Generic;
using System.Configuration;
using System.Linq; 


namespace WindowsFormsApp1
{
    public partial class MainFrm : Form
    {
        private string connectionString = ConfigurationManager.ConnectionStrings["MyConnectionString"].ConnectionString;
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
            //GetData("SELECT * FROM Khoa");
            //GetData("SELECT * FROM SinhVien");
            GetData("SELECT * FROM MonHoc");
            //GetData("SELECT * FROM KetQua");
            //GetData("SELECT * FROM DangNhap");
            dtgvMonHoc.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill; 
        }

        private void btnThem_Click(object sender, EventArgs e)
        {
            EnableControls(new List<Control> { txtMaMH, TxtTenMH, txtSoTin, btnLuu });
            ResetText(new List<Control> { txtMaMH, TxtTenMH, txtSoTin });
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
            string maMH = txtMaMH.Text.Trim();
            string tenMh = TxtTenMH.Text.Trim();
            string soTin = txtSoTin.Text.Trim();

            // Kiểm tra nếu có trường nào còn trống
            if (string.IsNullOrEmpty(maMH) || string.IsNullOrEmpty(tenMh) || string.IsNullOrEmpty(soTin))
            {
                MessageBox.Show("Vui lòng nhập đầy đủ thông tin.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Kiểm tra tên môn học chỉ chứa chữ và khoảng trắng
            if (!tenMh.All(c => char.IsLetter(c) || char.IsWhiteSpace(c)))
            {
                MessageBox.Show("Tên môn học phải là định dạng chữ.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            // Kiểm tra mã môn học và số tín chỉ phải là số hợp lệ và không âm
            if (!int.TryParse(maMH, out _) || !int.TryParse(soTin, out int soTinValue) || soTinValue < 0 || int.Parse(maMH) < 0)
            {
                MessageBox.Show("Mã môn học và Số tín chỉ phải là số hợp lệ và không được là số âm.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            string checkQuery = @"SELECT COUNT(*) 
                          FROM MonHoc 
                          WHERE MaMH = @MaMH OR (TenMH = @TenMH AND SoTin = @SoTin)";
            string insertQuery = "INSERT INTO MonHoc (MaMH, TenMH, SoTin) VALUES (@MaMH, @TenMH, @SoTin)";

            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();

                    // Kiểm tra trùng lặp dữ liệu
                    using (var checkCmd = new SqlCommand(checkQuery, conn))
                    {
                        checkCmd.Parameters.AddWithValue("@MaMH", maMH);
                        checkCmd.Parameters.AddWithValue("@TenMH", tenMh);
                        checkCmd.Parameters.AddWithValue("@SoTin", soTinValue);

                        int count = (int)checkCmd.ExecuteScalar();
                        if (count > 0)
                        {
                            MessageBox.Show("Dữ liệu đã tồn tại. Vui lòng kiểm tra lại.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                            return;
                        }
                    }

                    // Thêm mới môn học nếu không có trùng lặp
                    using (var cmd = new SqlCommand(insertQuery, conn))
                    {
                        cmd.Parameters.AddWithValue("@MaMH", maMH);
                        cmd.Parameters.AddWithValue("@TenMH", tenMh);
                        cmd.Parameters.AddWithValue("@SoTin", soTinValue);

                        int kq = cmd.ExecuteNonQuery();

                        if (kq > 0)
                        {
                            MessageBox.Show("Thêm môn học thành công.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Information);
                            LoadTableMonHoc();
                            UnenableControl(new List<Control> { txtMaMH, TxtTenMH, txtSoTin, btnLuu });
                            ResetText(new List<Control> { txtMaMH, TxtTenMH, txtSoTin });
                        }
                        else
                        {
                            MessageBox.Show("Không thể thêm môn học, vui lòng xem lại.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        }
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Có lỗi xảy ra: {ex.Message}", "Lỗi", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }







        private void btnHienThiTatCa_Click(object sender, EventArgs e)
        {
            CapNhatDiemSinhVien f = new CapNhatDiemSinhVien();
            f.ShowDialog();
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
                txtSoTin.Text = dtgvMonHoc.Rows[e.RowIndex].Cells[dtgvMonHoc.Columns["SoTin"].Index].Value.ToString(); 
                EnableControls(new List<Control> { txtSoTin, txtMaMH, TxtTenMH, btnXoa, btnSua });
            }
        }

        private void btnSua_Click(object sender, EventArgs e)
        {
            string maMH = txtMaMH.Text.Trim();
            string tenMH = TxtTenMH.Text.Trim();
            string soTin = txtSoTin.Text.Trim();

          
            if (string.IsNullOrEmpty(maMH) || string.IsNullOrEmpty(tenMH) || string.IsNullOrEmpty(soTin))
            {
                MessageBox.Show("Vui lòng nhập đầy đủ thông tin.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

           
            if (!int.TryParse(maMH, out _))
            {
                MessageBox.Show("Mã môn học phải là số hợp lệ.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

           
            if (!tenMH.All(c => char.IsLetter(c) || char.IsWhiteSpace(c)))
            {
                MessageBox.Show("Tên môn học phải là chữ cái.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

           
            if (!int.TryParse(soTin, out _))
            {
                MessageBox.Show("Số tín chỉ phải là số hợp lệ.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

           
            string checkMaMHQuery = @"SELECT COUNT(*) 
                               FROM MonHoc 
                               WHERE MaMH = @MaMH AND MaMH != @CurrentMaMH";

           
            string checkTenMHQuery = @"SELECT COUNT(*) 
                               FROM MonHoc 
                               WHERE TenMH = @TenMH AND MaMH != @CurrentMaMH";

            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();

                    
                    using (var checkMaMHCmd = new SqlCommand(checkMaMHQuery, conn))
                    {
                        checkMaMHCmd.Parameters.AddWithValue("@MaMH", maMH);
                        checkMaMHCmd.Parameters.AddWithValue("@CurrentMaMH", maMH);

                        int countMaMH = (int)checkMaMHCmd.ExecuteScalar(); 
                        if (countMaMH > 0)
                        {
                            MessageBox.Show("Mã môn học đã tồn tại. Vui lòng kiểm tra lại.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                            return;
                        }
                    }

                    
                    using (var checkTenMHCmd = new SqlCommand(checkTenMHQuery, conn))
                    {
                        checkTenMHCmd.Parameters.AddWithValue("@TenMH", tenMH);
                        checkTenMHCmd.Parameters.AddWithValue("@CurrentMaMH", maMH);

                        int countTenMH = (int)checkTenMHCmd.ExecuteScalar(); 
                        if (countTenMH > 0)
                        {
                            MessageBox.Show("Tên môn học đã tồn tại. Vui lòng kiểm tra lại.", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                            return;
                        }
                    }

                  
                    string query = $"UPDATE MonHoc SET TenMH = N'{tenMH}', SoTin = {soTin} WHERE MaMH = '{maMH}'";
                    int kq = DataProvider.ThaoTacCSDL(query);

                    if (kq > 0)
                    {
                        MessageBox.Show("Sửa môn học thành công", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Information);
                        LoadTableMonHoc();
                        UnenableControl(new List<Control> { txtMaMH, TxtTenMH, txtSoTin, btnLuu, btnSua, btnXoa });
                        ResetText(new List<Control> { txtMaMH, TxtTenMH, txtSoTin });
                    }
                    else
                    {
                        MessageBox.Show("Không thể sửa môn học, vui lòng xem lại", "Thông báo", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Có lỗi xảy ra: {ex.Message}", "Lỗi", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }


        private void btnXoa_Click(object sender, EventArgs e)
        {
            string maMH = txtMaMH.Text; string query = $"DELETE MonHoc Where MaMH = '{maMH}'";
            int kq = DataProvider.ThaoTacCSDL(query);
            if (kq > 0)
            {
                MessageBox.Show("Xóa môn học thành công");
                LoadTableMonHoc();
                UnenableControl(new List<Control> { txtMaMH, TxtTenMH, txtSoTin, btnLuu, btnSua, btnXoa });
                ResetText(new List<Control> { txtMaMH, TxtTenMH, txtSoTin });
            }
            else
            {
                MessageBox.Show("Không thể xóa môn học, vui lòng xem lại");
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

        private void btnTimMHTheoND_Click(object sender, EventArgs e)
        {
            string tuKhoa = txtNoiDung.Text;
            string query = $"Select * from MonHoc Where tenMH LIKE N'%{tuKhoa}%'";
            dt.Clear();
            dt = DataProvider.LoadCSDL(query);
            dtgvMonHoc.DataSource = dt;
        }
        

        private void btn_doimk_Click(object sender, EventArgs e)
        {
            Doimatkau formDoiMatKhau = new Doimatkau();
            formDoiMatKhau.ShowDialog();
        }
        
        private void btnCapNhatKhoa_Click(object sender, EventArgs e)
        {
        }

        private void btnCapNhatSV_Click(object sender, EventArgs e)
        {
            CapNhatSinhVien f = new CapNhatSinhVien();
            f.ShowDialog();
        }

        private void dtgvMonHoc_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            if (e.RowIndex >= 0)
            {
                txtMaMH.Text = dtgvMonHoc.Rows[e.RowIndex].Cells[0].Value.ToString();
                TxtTenMH.Text = dtgvMonHoc.Rows[e.RowIndex].Cells[1].Value.ToString();
                txtSoTin.Text = dtgvMonHoc.Rows[e.RowIndex].Cells[2].Value.ToString();
                EnableControls(new List<Control> { txtSoTin, txtMaMH, TxtTenMH, btnXoa, btnSua });
            }
        }

        private void btnHienThiAll_Click(object sender, EventArgs e)
        {
            GetData("select * from MonHoc");
        }
    }
}