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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(MainFrm));
            this.comboMaMH = new System.Windows.Forms.ComboBox();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.label5 = new System.Windows.Forms.Label();
            this.label6 = new System.Windows.Forms.Label();
            this.txtMaMH = new System.Windows.Forms.TextBox();
            this.TxtTenMH = new System.Windows.Forms.TextBox();
            this.txtSoTin = new System.Windows.Forms.TextBox();
            this.txtNoiDung = new System.Windows.Forms.TextBox();
            this.btnTimMHTheoND = new System.Windows.Forms.Button();
            this.btnTimMonHocTheoMa = new System.Windows.Forms.Button();
            this.btnCapNhatDiemSV = new System.Windows.Forms.Button();
            this.dtgvMonHoc = new System.Windows.Forms.DataGridView();
            this.Column1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Column2 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Column3 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.btnThem = new System.Windows.Forms.Button();
            this.btnLuu = new System.Windows.Forms.Button();
            this.btnSua = new System.Windows.Forms.Button();
            this.btnXoa = new System.Windows.Forms.Button();
            this.btn_doimk = new System.Windows.Forms.Button();
            this.btnCapNhatSV = new System.Windows.Forms.Button();
            this.btnHienThiAll = new System.Windows.Forms.Button();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.pictureBox1 = new System.Windows.Forms.PictureBox();
            ((System.ComponentModel.ISupportInitialize)(this.dtgvMonHoc)).BeginInit();
            this.groupBox1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).BeginInit();
            this.SuspendLayout();
            // 
            // comboMaMH
            // 
            this.comboMaMH.FormattingEnabled = true;
            this.comboMaMH.Location = new System.Drawing.Point(525, 114);
            this.comboMaMH.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.comboMaMH.Name = "comboMaMH";
            this.comboMaMH.Size = new System.Drawing.Size(248, 32);
            this.comboMaMH.TabIndex = 2;
            this.comboMaMH.Click += new System.EventHandler(this.comboMaMH_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.Location = new System.Drawing.Point(6, 56);
            this.label1.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(112, 24);
            this.label1.TabIndex = 0;
            this.label1.Text = "Mã môn học";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label2.Location = new System.Drawing.Point(5, 123);
            this.label2.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(116, 24);
            this.label2.TabIndex = 0;
            this.label2.Text = "Tên môn học";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label3.Location = new System.Drawing.Point(6, 193);
            this.label3.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(59, 24);
            this.label3.TabIndex = 0;
            this.label3.Text = "Số tín";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label4.Location = new System.Drawing.Point(520, 82);
            this.label4.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(240, 24);
            this.label4.TabIndex = 0;
            this.label4.Text = "Chọn mã môn học cần tìm :";
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.BackColor = System.Drawing.Color.AliceBlue;
            this.label5.Font = new System.Drawing.Font("Stencil", 24F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label5.ForeColor = System.Drawing.SystemColors.Desktop;
            this.label5.Location = new System.Drawing.Point(419, 17);
            this.label5.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(332, 38);
            this.label5.TabIndex = 0;
            this.label5.Text = "Quản lý thông tin";
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label6.Location = new System.Drawing.Point(520, 222);
            this.label6.Margin = new System.Windows.Forms.Padding(4, 0, 4, 0);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(138, 24);
            this.label6.TabIndex = 0;
            this.label6.Text = "Nhập từ khoá :";
            // 
            // txtMaMH
            // 
            this.txtMaMH.AcceptsReturn = true;
            this.txtMaMH.Enabled = false;
            this.txtMaMH.HideSelection = false;
            this.txtMaMH.Location = new System.Drawing.Point(149, 56);
            this.txtMaMH.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.txtMaMH.Name = "txtMaMH";
            this.txtMaMH.Size = new System.Drawing.Size(213, 27);
            this.txtMaMH.TabIndex = 1;
            // 
            // TxtTenMH
            // 
            this.TxtTenMH.Enabled = false;
            this.TxtTenMH.Location = new System.Drawing.Point(149, 114);
            this.TxtTenMH.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.TxtTenMH.Name = "TxtTenMH";
            this.TxtTenMH.Size = new System.Drawing.Size(296, 27);
            this.TxtTenMH.TabIndex = 1;
            // 
            // txtSoTin
            // 
            this.txtSoTin.Enabled = false;
            this.txtSoTin.Location = new System.Drawing.Point(149, 184);
            this.txtSoTin.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.txtSoTin.Name = "txtSoTin";
            this.txtSoTin.Size = new System.Drawing.Size(213, 27);
            this.txtSoTin.TabIndex = 1;
            // 
            // txtNoiDung
            // 
            this.txtNoiDung.Location = new System.Drawing.Point(525, 252);
            this.txtNoiDung.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.txtNoiDung.Name = "txtNoiDung";
            this.txtNoiDung.Size = new System.Drawing.Size(285, 27);
            this.txtNoiDung.TabIndex = 1;
            // 
            // btnTimMHTheoND
            // 
            this.btnTimMHTheoND.Location = new System.Drawing.Point(525, 292);
            this.btnTimMHTheoND.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btnTimMHTheoND.Name = "btnTimMHTheoND";
            this.btnTimMHTheoND.Size = new System.Drawing.Size(167, 41);
            this.btnTimMHTheoND.TabIndex = 3;
            this.btnTimMHTheoND.Text = "Tìm kiếm";
            this.btnTimMHTheoND.UseVisualStyleBackColor = true;
            this.btnTimMHTheoND.Click += new System.EventHandler(this.btnTimMHTheoND_Click);
            // 
            // btnTimMonHocTheoMa
            // 
            this.btnTimMonHocTheoMa.Location = new System.Drawing.Point(525, 165);
            this.btnTimMonHocTheoMa.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btnTimMonHocTheoMa.Name = "btnTimMonHocTheoMa";
            this.btnTimMonHocTheoMa.Size = new System.Drawing.Size(141, 41);
            this.btnTimMonHocTheoMa.TabIndex = 3;
            this.btnTimMonHocTheoMa.Text = "Tìm kiếm";
            this.btnTimMonHocTheoMa.UseVisualStyleBackColor = true;
            this.btnTimMonHocTheoMa.Click += new System.EventHandler(this.btnTimMonHocTheoMa_Click);
            // 
            // btnCapNhatDiemSV
            // 
            this.btnCapNhatDiemSV.Location = new System.Drawing.Point(868, 270);
            this.btnCapNhatDiemSV.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btnCapNhatDiemSV.Name = "btnCapNhatDiemSV";
            this.btnCapNhatDiemSV.Size = new System.Drawing.Size(249, 41);
            this.btnCapNhatDiemSV.TabIndex = 3;
            this.btnCapNhatDiemSV.Text = "Cập nhật Điểm Sinh Viên";
            this.btnCapNhatDiemSV.UseVisualStyleBackColor = true;
            this.btnCapNhatDiemSV.Click += new System.EventHandler(this.btnHienThiTatCa_Click);
            // 
            // dtgvMonHoc
            // 
            this.dtgvMonHoc.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dtgvMonHoc.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.Column1,
            this.Column2,
            this.Column3});
            this.dtgvMonHoc.Location = new System.Drawing.Point(35, 357);
            this.dtgvMonHoc.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.dtgvMonHoc.Name = "dtgvMonHoc";
            this.dtgvMonHoc.Size = new System.Drawing.Size(1050, 307);
            this.dtgvMonHoc.TabIndex = 4;
            this.dtgvMonHoc.CellClick += new System.Windows.Forms.DataGridViewCellEventHandler(this.dtgvMonHoc_CellClick);
            // 
            // Column1
            // 
            this.Column1.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.Fill;
            this.Column1.DataPropertyName = "MaMH";
            this.Column1.HeaderText = "Mã Môn Học";
            this.Column1.Name = "Column1";
            // 
            // Column2
            // 
            this.Column2.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.Fill;
            this.Column2.DataPropertyName = "TenMH";
            this.Column2.HeaderText = "Tên Môn Học";
            this.Column2.Name = "Column2";
            // 
            // Column3
            // 
            this.Column3.AutoSizeMode = System.Windows.Forms.DataGridViewAutoSizeColumnMode.Fill;
            this.Column3.DataPropertyName = "SoTin";
            this.Column3.HeaderText = "Số Tín";
            this.Column3.Name = "Column3";
            // 
            // btnThem
            // 
            this.btnThem.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold);
            this.btnThem.Location = new System.Drawing.Point(229, 678);
            this.btnThem.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btnThem.Name = "btnThem";
            this.btnThem.Size = new System.Drawing.Size(137, 42);
            this.btnThem.TabIndex = 5;
            this.btnThem.Text = "Thêm mới";
            this.btnThem.UseVisualStyleBackColor = true;
            this.btnThem.Click += new System.EventHandler(this.btnThem_Click);
            // 
            // btnLuu
            // 
            this.btnLuu.Enabled = false;
            this.btnLuu.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold);
            this.btnLuu.Location = new System.Drawing.Point(392, 678);
            this.btnLuu.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btnLuu.Name = "btnLuu";
            this.btnLuu.Size = new System.Drawing.Size(137, 42);
            this.btnLuu.TabIndex = 5;
            this.btnLuu.Text = "Lưu ";
            this.btnLuu.UseVisualStyleBackColor = true;
            this.btnLuu.Click += new System.EventHandler(this.btnLuu_Click);
            // 
            // btnSua
            // 
            this.btnSua.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold);
            this.btnSua.Location = new System.Drawing.Point(558, 678);
            this.btnSua.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btnSua.Name = "btnSua";
            this.btnSua.Size = new System.Drawing.Size(137, 42);
            this.btnSua.TabIndex = 5;
            this.btnSua.Text = "Sửa";
            this.btnSua.UseVisualStyleBackColor = true;
            this.btnSua.Click += new System.EventHandler(this.btnSua_Click);
            // 
            // btnXoa
            // 
            this.btnXoa.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold);
            this.btnXoa.Location = new System.Drawing.Point(728, 678);
            this.btnXoa.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btnXoa.Name = "btnXoa";
            this.btnXoa.Size = new System.Drawing.Size(137, 42);
            this.btnXoa.TabIndex = 5;
            this.btnXoa.Text = "Xoá";
            this.btnXoa.UseVisualStyleBackColor = true;
            this.btnXoa.Click += new System.EventHandler(this.btnXoa_Click);
            // 
            // btn_doimk
            // 
            this.btn_doimk.Location = new System.Drawing.Point(15, 14);
            this.btn_doimk.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btn_doimk.Name = "btn_doimk";
            this.btn_doimk.Size = new System.Drawing.Size(240, 41);
            this.btn_doimk.TabIndex = 6;
            this.btn_doimk.Text = "Đổi mật khẩu";
            this.btn_doimk.UseVisualStyleBackColor = true;
            this.btn_doimk.Click += new System.EventHandler(this.btn_doimk_Click);
            // 
            // btnCapNhatSV
            // 
            this.btnCapNhatSV.Location = new System.Drawing.Point(868, 222);
            this.btnCapNhatSV.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btnCapNhatSV.Name = "btnCapNhatSV";
            this.btnCapNhatSV.Size = new System.Drawing.Size(202, 41);
            this.btnCapNhatSV.TabIndex = 7;
            this.btnCapNhatSV.Text = "Cập nhật sinh viên";
            this.btnCapNhatSV.UseVisualStyleBackColor = true;
            this.btnCapNhatSV.Click += new System.EventHandler(this.btnCapNhatSV_Click);
            // 
            // btnHienThiAll
            // 
            this.btnHienThiAll.Location = new System.Drawing.Point(868, 173);
            this.btnHienThiAll.Margin = new System.Windows.Forms.Padding(4, 3, 4, 3);
            this.btnHienThiAll.Name = "btnHienThiAll";
            this.btnHienThiAll.Size = new System.Drawing.Size(166, 41);
            this.btnHienThiAll.TabIndex = 8;
            this.btnHienThiAll.Text = "Hiển Thị Tất Cả";
            this.btnHienThiAll.UseVisualStyleBackColor = true;
            this.btnHienThiAll.Click += new System.EventHandler(this.btnHienThiAll_Click);
            // 
            // groupBox1
            // 
            this.groupBox1.BackColor = System.Drawing.Color.AliceBlue;
            this.groupBox1.Controls.Add(this.label1);
            this.groupBox1.Controls.Add(this.label2);
            this.groupBox1.Controls.Add(this.label3);
            this.groupBox1.Controls.Add(this.txtMaMH);
            this.groupBox1.Controls.Add(this.TxtTenMH);
            this.groupBox1.Controls.Add(this.txtSoTin);
            this.groupBox1.Location = new System.Drawing.Point(26, 61);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(467, 272);
            this.groupBox1.TabIndex = 9;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Quản lý môn học";
            // 
            // pictureBox1
            // 
            this.pictureBox1.BackColor = System.Drawing.Color.AliceBlue;
            this.pictureBox1.Image = ((System.Drawing.Image)(resources.GetObject("pictureBox1.Image")));
            this.pictureBox1.Location = new System.Drawing.Point(743, 5);
            this.pictureBox1.Name = "pictureBox1";
            this.pictureBox1.Size = new System.Drawing.Size(100, 50);
            this.pictureBox1.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.pictureBox1.TabIndex = 10;
            this.pictureBox1.TabStop = false;
            // 
            // MainFrm
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(11F, 24F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.AliceBlue;
            this.ClientSize = new System.Drawing.Size(1137, 795);
            this.Controls.Add(this.pictureBox1);
            this.Controls.Add(this.btnHienThiAll);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.btn_doimk);
            this.Controls.Add(this.btnCapNhatSV);
            this.Controls.Add(this.btnXoa);
            this.Controls.Add(this.dtgvMonHoc);
            this.Controls.Add(this.btnSua);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.btnLuu);
            this.Controls.Add(this.label6);
            this.Controls.Add(this.btnThem);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.comboMaMH);
            this.Controls.Add(this.txtNoiDung);
            this.Controls.Add(this.btnTimMHTheoND);
            this.Controls.Add(this.btnCapNhatDiemSV);
            this.Controls.Add(this.btnTimMonHocTheoMa);
            this.Font = new System.Drawing.Font("Sitka Small", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.Margin = new System.Windows.Forms.Padding(5, 6, 5, 6);
            this.Name = "MainFrm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = " ";
            this.Load += new System.EventHandler(this.MainFrm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dtgvMonHoc)).EndInit();
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).EndInit();
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
        private System.Windows.Forms.TextBox TxtTenMH;
        private System.Windows.Forms.TextBox txtSoTin;
        private System.Windows.Forms.TextBox txtNoiDung;
        private System.Windows.Forms.Button btnTimMHTheoND;
        private System.Windows.Forms.Button btnTimMonHocTheoMa;
        private System.Windows.Forms.Button btnCapNhatDiemSV;
        private System.Windows.Forms.DataGridView dtgvMonHoc;
        private System.Windows.Forms.Button btnThem;
        private System.Windows.Forms.Button btnLuu;
        private System.Windows.Forms.Button btnSua;
        private System.Windows.Forms.Button btnXoa;
        public System.Windows.Forms.TextBox txtMaMH;
        private System.Windows.Forms.ComboBox comboMaMH;
        private System.Windows.Forms.Button btn_doimk;
        private System.Windows.Forms.Button btnCapNhatSV;
        private System.Windows.Forms.Button btnHienThiAll;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.PictureBox pictureBox1;
        private System.Windows.Forms.DataGridViewTextBoxColumn Column1;
        private System.Windows.Forms.DataGridViewTextBoxColumn Column2;
        private System.Windows.Forms.DataGridViewTextBoxColumn Column3;
    }
}