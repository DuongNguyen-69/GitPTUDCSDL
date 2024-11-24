using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Reporting.WinForms;
namespace WindowsFormsApp1
{
    public partial class reportFrm : Form
    {
        private string Option;
        public reportFrm(string option)
        {
            InitializeComponent();
            Option = option;
        }

        private void reportFrm_Load(object sender, EventArgs e)
        {
            if (Option == "XemDSSV")
            {
                try
                {
                    reportViewer1.LocalReport.ReportEmbeddedResource = "WindowsFormsApp1.ReportSV.rdlc";
                    string query = @"select MaSV, HoTen, Format(NgaySinh,'dd/MM/yyy') As NgaySinh,
                        GioiTinh, DiaChi, DienThoai, MaKhoa from SinhVien;";
                    ReportDataSource reportDataSource = new ReportDataSource()
                    {
                        Name = "DataSetSV",
                        Value = DataProvider.LoadCSDL(query)
                    };
                    this.reportViewer1.LocalReport.DataSources.Add(reportDataSource);

                }
                catch(Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }

            else if (Option == "XemDSSVTheoKhoa")
            {
                try
                {
                    reportViewer1.LocalReport.ReportEmbeddedResource = "WindowsFormsApp1.ReportSVTheoKhoa.rdlc";
                    string query1 = @"select 
                                    	sv.MaSV,
	                                    sv.HoTen,
                                      	FORMAT (sv.NgaySinh,'dd/MM/yyy')as NgaySinh,
	                                    sv.GioiTinh,
	                                    sv.DiaChi,
	                                    sv.DienThoai
                                    from
	                                    SinhVien sv join Khoa k on sv.MaKhoa = K.MaKhoa
                                    order by k.TenKhoa";
                    string query2 = @"select 
	                                    k.TenKhoa
                                    from
	                                    SinhVien sv join Khoa k on sv.MaKhoa = K.MaKhoa
                                    order by k.TenKhoa";




                    var reportDataSource1 = new ReportDataSource()
                    {
                        Name = "DataSetSV",
                        Value = DataProvider.LoadCSDL(query1)
                    };
                    var reportDataSource2 = new ReportDataSource()
                    {
                        Name = "DataSet1",
                        Value = DataProvider.LoadCSDL(query2)
                    };
                    reportViewer1.LocalReport.DataSources.Add(reportDataSource1);
                    reportViewer1.LocalReport.DataSources.Add(reportDataSource2);
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
            else if(Option == "XemDiem")
            {
                try
                {
                    reportViewer1.LocalReport.ReportEmbeddedResource = "WindowsFormsApp1.ReportXemDiem.rdlc";
                    string query = "select * from KetQua";

                    ReportDataSource reportDataSource = new ReportDataSource()
                    {
                        Name = "DataSetDiem",
                        Value = DataProvider.LoadCSDL(query)
                    };
                    this.reportViewer1.LocalReport.DataSources.Add(reportDataSource);

                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }
            

            else if(Option == "XemDiemTheoMon")
            {
                try
                {
                    reportViewer1.LocalReport.ReportEmbeddedResource = "WindowsFormsApp1.ReportDiemTheoMon.rdlc";
                    string query1 = @"select 
	                                    k.MaSV,k.MaMH,k.Diem
                                    from MonHoc m join KetQua k on m.MaMH=k.MaMH
                                    order by m.TenMH ";
                    string  query2 = @"select   
	                                        m.TenMH
                                       from MonHoc m join KetQua k on m.MaMH=k.MaMH
                                       order by m.TenMH ";
                    var dataResource1 = new ReportDataSource()
                    {
                        Name = "DataSetDiem",
                        Value = DataProvider.LoadCSDL(query1)
                    };
                    var dataResource2 = new ReportDataSource()
                    {
                        Name = "DataSetMonHoc",
                        Value = DataProvider.LoadCSDL(query2)
                    };
                    reportViewer1.LocalReport.DataSources.Add(dataResource1);
                    reportViewer1.LocalReport.DataSources.Add(dataResource2);
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message);
                }
            }



            this.reportViewer1.RefreshReport();
        }
    }
}
