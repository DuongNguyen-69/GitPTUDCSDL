using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data.SqlClient;
using System.Data.Common;
using System.Data;
using System.Configuration;
namespace WindowsFormsApp1
{
    internal class DataBase
    {
        private string connectionString = ConfigurationManager.ConnectionStrings["MyConnectionString"].ConnectionString;
        SqlConnection conn = null;
        SqlDataAdapter da = null;
        DataSet ds = null;
        public DataBase()
        {
            conn = new SqlConnection(connectionString);
        }
        //Ham lay du lieu
        public DataTable LayDL(string sqlStr)
        {
            da = new SqlDataAdapter(sqlStr, conn);
            ds = new DataSet();
            da.Fill(ds);
            return ds.Tables[0];
        }
        //Ham thuc thi cau lenh them sua xoa
        public void ThucThi(string sqlStr)
        {
            SqlCommand cmd = new SqlCommand(sqlStr, conn);
            conn.Open();
            cmd.ExecuteNonQuery();
            conn.Close();
        }

        public DataTable Kiemtra(string sqlStr)
        {
            DataTable dt = new DataTable();
            conn.Open();
            SqlCommand cmd = new SqlCommand(sqlStr, conn);
            SqlDataAdapter da = new SqlDataAdapter(cmd);
            da.Fill(dt);
            conn.Close();
            return dt;
        }


        //Ham hien thi ket qua tim kiem
        public DataTable ParticularRows(string sqlStr)
        {
            DataTable dt = new DataTable();

            using (SqlConnection conn = new SqlConnection(connectionString))
            {
                using (SqlCommand cmd = new SqlCommand(sqlStr, conn))
                {
                    conn.Open();
                    using (SqlDataAdapter da = new SqlDataAdapter(cmd))
                    {
                        da.Fill(dt);
                    }
                }
            }

            return dt;
        }


    }
}
