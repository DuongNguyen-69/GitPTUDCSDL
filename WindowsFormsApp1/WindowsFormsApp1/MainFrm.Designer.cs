namespace WindowsFormsApp1
{
    partial class MainFrm
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            System.Windows.Forms.ComboBox comboMaMH;
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.label5 = new System.Windows.Forms.Label();
            this.label6 = new System.Windows.Forms.Label();
            this.txtMaMH = new System.Windows.Forms.TextBox();
            this.TxtTenMH = new System.Windows.Forms.TextBox();
            this.txtSoTiet = new System.Windows.Forms.TextBox();
            this.txtNoiDung = new System.Windows.Forms.TextBox();
            this.btnTimMHTheoND = new System.Windows.Forms.Button();
            this.btnTimMonHocTheoMa = new System.Windows.Forms.Button();
            this.btnHienThiTatCa = new System.Windows.Forms.Button();
            this.dtgvMonHoc = new System.Windows.Forms.DataGridView();
            this.btnThem = new System.Windows.Forms.Button();
            this.btnLuu = new System.Windows.Forms.Button();
            this.btnSua = new System.Windows.Forms.Button();
            this.btnXoa = new System.Windows.Forms.Button();
            this.btnXemDSSV = new System.Windows.Forms.Button();
            this.btnXemDSSVTheoKhoa = new System.Windows.Forms.Button();
            this.btnXemDiem = new System.Windows.Forms.Button();
            this.btnXemDiemTheoMon = new System.Windows.Forms.Button();
            comboMaMH = new System.Windows.Forms.ComboBox();
            ((System.ComponentModel.ISupportInitialize)(this.dtgvMonHoc)).BeginInit();
            this.SuspendLayout();
            // 
            // comboMaMH
            // 
            comboMaMH.FormattingEnabled = true;
            comboMaMH.Location = new System.Drawing.Point(482, 133);
            comboMaMH.Name = "comboMaMH";
            comboMaMH.Size = new System.Drawing.Size(204, 40);
            comboMaMH.TabIndex = 2;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(105, 56);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(151, 32);
            this.label1.TabIndex = 0;
            this.label1.Text = "Mã môn học";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(105, 133);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(155, 32);
            this.label2.TabIndex = 0;
            this.label2.Text = "Tên môn học";
            this.label2.Click += new System.EventHandler(this.label2_Click);
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(105, 238);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(84, 32);
            this.label3.TabIndex = 0;
            this.label3.Text = "Số tiết";
            this.label3.Click += new System.EventHandler(this.label3_Click);
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(486, 76);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(312, 32);
            this.label4.TabIndex = 0;
            this.label4.Text = "Chọn mã môn học cần tìm :";
            this.label4.Click += new System.EventHandler(this.label4_Click);
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Font = new System.Drawing.Font("Segoe UI", 21.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label5.ForeColor = System.Drawing.SystemColors.HotTrack;
            this.label5.Location = new System.Drawing.Point(878, 41);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(423, 60);
            this.label5.TabIndex = 0;
            this.label5.Text = "Tìm kiếm thông tin";
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(729, 133);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(173, 32);
            this.label6.TabIndex = 0;
            this.label6.Text = "Nhập từ khoá :";
            // 
            // txtMaMH
            // 
            this.txtMaMH.Enabled = false;
            this.txtMaMH.Location = new System.Drawing.Point(254, 56);
            this.txtMaMH.Name = "txtMaMH";
            this.txtMaMH.Size = new System.Drawing.Size(175, 39);
            this.txtMaMH.TabIndex = 1;
            // 
            // TxtTenMH
            // 
            this.TxtTenMH.Enabled = false;
            this.TxtTenMH.Location = new System.Drawing.Point(254, 133);
            this.TxtTenMH.Name = "TxtTenMH";
            this.TxtTenMH.Size = new System.Drawing.Size(175, 39);
            this.TxtTenMH.TabIndex = 1;
            // 
            // txtSoTiet
            // 
            this.txtSoTiet.Enabled = false;
            this.txtSoTiet.Location = new System.Drawing.Point(254, 230);
            this.txtSoTiet.Name = "txtSoTiet";
            this.txtSoTiet.Size = new System.Drawing.Size(175, 39);
            this.txtSoTiet.TabIndex = 1;
            // 
            // txtNoiDung
            // 
            this.txtNoiDung.Location = new System.Drawing.Point(885, 133);
            this.txtNoiDung.Name = "txtNoiDung";
            this.txtNoiDung.Size = new System.Drawing.Size(234, 39);
            this.txtNoiDung.TabIndex = 1;
            this.txtNoiDung.TextChanged += new System.EventHandler(this.txtNoiDung_TextChanged);
            // 
            // btnTimMHTheoND
            // 
            this.btnTimMHTheoND.Location = new System.Drawing.Point(943, 200);
            this.btnTimMHTheoND.Name = "btnTimMHTheoND";
            this.btnTimMHTheoND.Size = new System.Drawing.Size(137, 36);
            this.btnTimMHTheoND.TabIndex = 3;
            this.btnTimMHTheoND.Text = "Tìm kiếm";
            this.btnTimMHTheoND.UseVisualStyleBackColor = true;
            // 
            // btnTimMonHocTheoMa
            // 
            this.btnTimMonHocTheoMa.Location = new System.Drawing.Point(521, 200);
            this.btnTimMonHocTheoMa.Name = "btnTimMonHocTheoMa";
            this.btnTimMonHocTheoMa.Size = new System.Drawing.Size(115, 36);
            this.btnTimMonHocTheoMa.TabIndex = 3;
            this.btnTimMonHocTheoMa.Text = "tìm kiếm";
            this.btnTimMonHocTheoMa.UseVisualStyleBackColor = true;
            // 
            // btnHienThiTatCa
            // 
            this.btnHienThiTatCa.Location = new System.Drawing.Point(88, 296);
            this.btnHienThiTatCa.Name = "btnHienThiTatCa";
            this.btnHienThiTatCa.Size = new System.Drawing.Size(115, 36);
            this.btnHienThiTatCa.TabIndex = 3;
            this.btnHienThiTatCa.Text = "Hiện ra tất cả";
            this.btnHienThiTatCa.UseVisualStyleBackColor = true;
            this.btnHienThiTatCa.Click += new System.EventHandler(this.btnHienThiTatCa_Click);
            // 
            // dtgvMonHoc
            // 
            this.dtgvMonHoc.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dtgvMonHoc.Location = new System.Drawing.Point(12, 351);
            this.dtgvMonHoc.Name = "dtgvMonHoc";
            this.dtgvMonHoc.Size = new System.Drawing.Size(1225, 269);
            this.dtgvMonHoc.TabIndex = 4;
            // 
            // btnThem
            // 
            this.btnThem.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnThem.Location = new System.Drawing.Point(70, 635);
            this.btnThem.Name = "btnThem";
            this.btnThem.Size = new System.Drawing.Size(112, 37);
            this.btnThem.TabIndex = 5;
            this.btnThem.Text = "Thêm mới";
            this.btnThem.UseVisualStyleBackColor = true;
            this.btnThem.Click += new System.EventHandler(this.btnThem_Click);
            // 
            // btnLuu
            // 
            this.btnLuu.Enabled = false;
            this.btnLuu.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnLuu.Location = new System.Drawing.Point(198, 635);
            this.btnLuu.Name = "btnLuu";
            this.btnLuu.Size = new System.Drawing.Size(112, 37);
            this.btnLuu.TabIndex = 5;
            this.btnLuu.Text = "Lưu ";
            this.btnLuu.UseVisualStyleBackColor = true;
            this.btnLuu.Click += new System.EventHandler(this.btnLuu_Click);
            // 
            // btnSua
            // 
            this.btnSua.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnSua.Location = new System.Drawing.Point(326, 635);
            this.btnSua.Name = "btnSua";
            this.btnSua.Size = new System.Drawing.Size(112, 37);
            this.btnSua.TabIndex = 5;
            this.btnSua.Text = "Sửa";
            this.btnSua.UseVisualStyleBackColor = true;
            // 
            // btnXoa
            // 
            this.btnXoa.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnXoa.Location = new System.Drawing.Point(454, 635);
            this.btnXoa.Name = "btnXoa";
            this.btnXoa.Size = new System.Drawing.Size(112, 37);
            this.btnXoa.TabIndex = 5;
            this.btnXoa.Text = "Xoá";
            this.btnXoa.UseVisualStyleBackColor = true;
            // 
            // btnXemDSSV
            // 
            this.btnXemDSSV.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnXemDSSV.Location = new System.Drawing.Point(582, 635);
            this.btnXemDSSV.Name = "btnXemDSSV";
            this.btnXemDSSV.Size = new System.Drawing.Size(112, 37);
            this.btnXemDSSV.TabIndex = 5;
            this.btnXemDSSV.Text = "Xem DSSV";
            this.btnXemDSSV.UseVisualStyleBackColor = true;
            // 
            // btnXemDSSVTheoKhoa
            // 
            this.btnXemDSSVTheoKhoa.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnXemDSSVTheoKhoa.Location = new System.Drawing.Point(710, 635);
            this.btnXemDSSVTheoKhoa.Name = "btnXemDSSVTheoKhoa";
            this.btnXemDSSVTheoKhoa.Size = new System.Drawing.Size(190, 37);
            this.btnXemDSSVTheoKhoa.TabIndex = 5;
            this.btnXemDSSVTheoKhoa.Text = "Xem DSSV theo khoa";
            this.btnXemDSSVTheoKhoa.UseVisualStyleBackColor = true;
            // 
            // btnXemDiem
            // 
            this.btnXemDiem.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnXemDiem.Location = new System.Drawing.Point(916, 635);
            this.btnXemDiem.Name = "btnXemDiem";
            this.btnXemDiem.Size = new System.Drawing.Size(112, 37);
            this.btnXemDiem.TabIndex = 5;
            this.btnXemDiem.Text = "Xem điểm";
            this.btnXemDiem.UseVisualStyleBackColor = true;
            // 
            // btnXemDiemTheoMon
            // 
            this.btnXemDiemTheoMon.Font = new System.Drawing.Font("Segoe UI", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.btnXemDiemTheoMon.Location = new System.Drawing.Point(1044, 635);
            this.btnXemDiemTheoMon.Name = "btnXemDiemTheoMon";
            this.btnXemDiemTheoMon.Size = new System.Drawing.Size(157, 37);
            this.btnXemDiemTheoMon.TabIndex = 5;
            this.btnXemDiemTheoMon.Text = "Xem điểm theo môn";
            this.btnXemDiemTheoMon.UseVisualStyleBackColor = true;
            // 
            // MainFrm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(13F, 32F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1249, 696);
            this.Controls.Add(this.btnXemDiemTheoMon);
            this.Controls.Add(this.btnXemDiem);
            this.Controls.Add(this.btnXemDSSVTheoKhoa);
            this.Controls.Add(this.btnXemDSSV);
            this.Controls.Add(this.btnXoa);
            this.Controls.Add(this.btnSua);
            this.Controls.Add(this.btnLuu);
            this.Controls.Add(this.btnThem);
            this.Controls.Add(this.dtgvMonHoc);
            this.Controls.Add(this.btnHienThiTatCa);
            this.Controls.Add(this.btnTimMonHocTheoMa);
            this.Controls.Add(this.btnTimMHTheoND);
            this.Controls.Add(comboMaMH);
            this.Controls.Add(this.txtNoiDung);
            this.Controls.Add(this.txtSoTiet);
            this.Controls.Add(this.TxtTenMH);
            this.Controls.Add(this.txtMaMH);
            this.Controls.Add(this.label6);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Font = new System.Drawing.Font("Segoe UI", 12F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.Name = "MainFrm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = " ";
            this.Load += new System.EventHandler(this.MainFrm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dtgvMonHoc)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.TextBox txtMaMH;
        private System.Windows.Forms.TextBox TxtTenMH;
        private System.Windows.Forms.TextBox txtSoTiet;
        private System.Windows.Forms.TextBox txtNoiDung;
        private System.Windows.Forms.Button btnTimMHTheoND;
        private System.Windows.Forms.Button btnTimMonHocTheoMa;
        private System.Windows.Forms.Button btnHienThiTatCa;
        private System.Windows.Forms.DataGridView dtgvMonHoc;
        private System.Windows.Forms.Button btnThem;
        private System.Windows.Forms.Button btnLuu;
        private System.Windows.Forms.Button btnSua;
        private System.Windows.Forms.Button btnXoa;
        private System.Windows.Forms.Button btnXemDSSV;
        private System.Windows.Forms.Button btnXemDSSVTheoKhoa;
        private System.Windows.Forms.Button btnXemDiem;
        private System.Windows.Forms.Button btnXemDiemTheoMon;
    }
}