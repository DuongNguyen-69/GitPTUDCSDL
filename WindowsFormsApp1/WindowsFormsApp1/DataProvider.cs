using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data.SqlClient;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Windows.Forms;
using System.Data.SqlTypes;
using System.Data.Sql;
using System.Data.Common;


namespace WindowsFormsApp1
{
    public class DataProvider
    {
        const string connString = "Data Source=MSI\SQLEXPRESS;Initial Catalog=baitaplon;User ID=sa;Password=12345";
        private static SqlConnection connection;
        public static List<DangNhap> DangNhaps = new List<DangNhap>();
        public static void openconnection()
        {
            connection = new SqlConnection(connString);
            connection.Open();




        }
        public static void Closeconnection()
        {
            
            connection.Close();
             
        }
        public static void GetAllDangNhap()
        {
            try
            {
                openconnection();
                string query = "Select * from DangNhap";
                SqlCommand Command = new SqlCommand(query,connection);
                SqlDataReader reader = Command.ExecuteReader();
                while (reader.Read())
                {
                    DangNhap dangNhap = new DangNhap();
                    dangNhap.TaiKhoan = reader["TenDangNhap"].ToString();
                    dangNhap.MatKhau = reader["MatKhau"].ToString();
                    dangNhap.HoTen = reader["Hoten"].ToString();
                    dangNhap.Quyen = reader["Quyen"].ToString();
                    DangNhaps.Add(dangNhap);


                }

            }
            catch (SqlException ex)
            {
                MessageBox.Show(ex.Message);
            }
            finally
            {
                Closeconnection();
            }
        }
    }
}
