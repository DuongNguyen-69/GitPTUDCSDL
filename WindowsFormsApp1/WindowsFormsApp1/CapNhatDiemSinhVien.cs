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
    public partial class CapNhatDiemSinhVien : Form
    {
        private string connectionString = ConfigurationManager.ConnectionStrings["MyConnectionString"].ConnectionString;
        public CapNhatDiemSinhVien()
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

                    dgvCapNhatDiemSinhVien.DataSource = dt;

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

        private void CapNhatDiemSinhVien_Load(object sender, EventArgs e)
        {
            GetData("select * from KetQua");
        }

        private void btnThem_Click(object sender, EventArgs e)
        {
            string query = @"insert into KetQua values (@MaSV, @MaMH, @Diem)";

            //BỎ TRỐNG TEXT
            if (txtMaSV.Text.Trim() == "")
            {
                MessageBox.Show("Bạn chưa nhập mã sinh viên");
                txtMaSV.Focus();
                return;
            }
            else if(!int.TryParse(txtMaSV.Text.Trim(), out int MaSV)){
                MessageBox.Show("mã sinh viên phải là số");
            }
            //MaMH
            if (txtMaMH.Text.Trim() == "")
            {
                MessageBox.Show("Bạn chưa nhập mã môn học");
                txtMaMH.Focus(); return;
            }
            else if(!int.TryParse(txtMaMH.Text.Trim(), out int MaMH)){
                MessageBox.Show("Mã môn học phải là số");
            }
            //Diem
            if (txtDiem.Text.Trim() == "")
            {
                MessageBox.Show("Bạn chưa nhập điểm");
            }
            else if(!double.TryParse(txtDiem.Text.Trim(), out double diem)){
                MessageBox.Show("Điểm phải là một số!");return;
            }
            else if (diem < 0 || diem > 10){
                MessageBox.Show("Điểm phải nằm trong khoảng từ 0 đến 10!");
                return;
            }

            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();
                    
                    //trùng lặp
                    string checkDuplicateQuery = $"SELECT COUNT(*) FROM KetQua WHERE MaSV = @MaSV AND MaMH = @MaMH";
                    using (var checkCmd = new SqlCommand(checkDuplicateQuery, conn))
                    {
                        checkCmd.Parameters.AddWithValue("@MaSV", txtMaSV.Text.Trim());
                        checkCmd.Parameters.AddWithValue("@MaMH", txtMaMH.Text.Trim());

                        int duplicateCount = (int)checkCmd.ExecuteScalar();

                        if (duplicateCount > 0)
                        {
                            MessageBox.Show("Mã sinh viên và mã môn học đã tồn tại. Vui lòng kiểm tra lại!");
                            return;
                        }
                    }
                    

                    //đẩy dữ liệu vào dgv
                    var com = new SqlCommand(query, conn);
                    com.Parameters.AddWithValue("@MaSV", txtMaSV.Text.Trim());
                    com.Parameters.AddWithValue("@MaMH", txtMaMH.Text.Trim());
                    com.Parameters.AddWithValue("@Diem", txtDiem.Text.Trim());
                    com.ExecuteNonQuery(); 
                    MessageBox.Show("Thêm thành công");
                    GetData("select * from KetQua"); 
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Có lỗi xảy ra: {ex.Message}");
                }
            }
        }



        private void btnSua_Click(object sender, EventArgs e)
        {
            string query = "update KetQua set Diem = @Diem where MaSV = @MaSV and MaMH = @MaMH";
            //BỎ TRỐNG TEXT
            if (txtMaSV.Text.Trim() == "")
            {
                MessageBox.Show("Bạn chưa sửa mã sinh viên");
                txtMaSV.Focus();
                return;
            }
            else if (!int.TryParse(txtMaSV.Text.Trim(), out int MaSV))
            {
                MessageBox.Show("mã sinh viên phải là số");
            }
            //MaMH
            if (txtMaMH.Text.Trim() == "")
            {
                MessageBox.Show("Bạn chưa sửa mã môn học");
                txtMaMH.Focus(); return;
            }
            else if (!int.TryParse(txtMaMH.Text.Trim(), out int MaMH))
            {
                MessageBox.Show("Mã môn học phải là số");
            }
            //Diem
            if (txtDiem.Text.Trim() == "")
            {
                MessageBox.Show("Bạn chưa sửa điểm");
            }
            else if (!double.TryParse(txtDiem.Text.Trim(), out double diem))
            {
                MessageBox.Show("Điểm phải là một số"); return;
            }
            else if (diem < 0 || diem > 10)
            {
                MessageBox.Show("Điểm phải nằm trong khoảng từ 0 đến 10");
                return;
            }


            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    conn.Open();



                    //trùng lặp
                    string checkDuplicateQuery = $"SELECT COUNT(*) FROM KetQua WHERE MaSV = @MaSV AND MaMH = @MaMH";
                    using (var checkCmd = new SqlCommand(checkDuplicateQuery, conn))
                    {
                        checkCmd.Parameters.AddWithValue("@MaSV", txtMaSV.Text.Trim());
                        checkCmd.Parameters.AddWithValue("@MaMH", txtMaMH.Text.Trim());

                        int duplicateCount = (int)checkCmd.ExecuteScalar();

                        if (duplicateCount > 0)
                        {
                            MessageBox.Show("Mã sinh viên và mã môn học đã tồn tại. Vui lòng kiểm tra lại!");
                            return;
                        }
                    }

                    var com = new SqlCommand(query, conn);
                    com.Parameters.AddWithValue("@MaSV", txtMaSV.Text.Trim());
                    com.Parameters.AddWithValue("@MaMH", txtMaMH.Text.Trim());
                    com.Parameters.AddWithValue("@Diem", txtDiem.Text.Trim());
                    com.ExecuteNonQuery();
                    MessageBox.Show("Sửa thành công");
                    GetData("select * from KetQua");
                }
                catch(Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
            
        }

        private void btnXoa_Click(object sender, EventArgs e)
        {
            string query = "delete from KetQua where MaSV = @MaSV and MaMH = @MaMH";
            using (var conn = new SqlConnection(connectionString))
            {
                try
                {
                    if(txtMaSV.Text.Trim() == "")
                    {
                        if (txtMaMH.Text.Trim() == "")
                        {
                            if (txtDiem.Text.Trim() == "")
                            {
                                MessageBox.Show("Không có dữ liệu để xoá");return;
                            }
                            conn.Open();
                            var com = new SqlCommand(query, conn);
                            com.Parameters.AddWithValue("@MaSV", txtMaSV.Text.Trim());
                            com.Parameters.AddWithValue("@MaMH", txtMaMH.Text.Trim());
                            com.ExecuteNonQuery();
                            MessageBox.Show("Xoá thành công");
                            GetData("select * from KetQua");
                        }
                    }
                    
                }
                catch(Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
        }

        private void dgvCapNhatDiemSinhVien_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            txtMaSV.Text = dgvCapNhatDiemSinhVien.Rows[e.RowIndex].Cells[0].Value.ToString();
            txtMaMH.Text = dgvCapNhatDiemSinhVien.Rows[e.RowIndex].Cells[1].Value.ToString();
            txtDiem.Text = dgvCapNhatDiemSinhVien.Rows[e.RowIndex].Cells[2].Value.ToString();
        }
        
    }
}