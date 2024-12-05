namespace WindowsFormsApp1
{
    partial class SuaMonHoc
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(SuaMonHoc));
            this.txtSoTin = new System.Windows.Forms.TextBox();
            this.TxtTenMH = new System.Windows.Forms.TextBox();
            this.txtMaMH = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.btnSuatimkiem = new System.Windows.Forms.Button();
            this.btnThoattimkiem = new System.Windows.Forms.Button();
            this.btnXoasuatimkiem = new System.Windows.Forms.Button();
            this.pictureBox1 = new System.Windows.Forms.PictureBox();
            this.label1 = new System.Windows.Forms.Label();
            this.dtgvMonHoc = new System.Windows.Forms.DataGridView();
            this.Column1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Column2 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.Column3 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.groupBox1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.dtgvMonHoc)).BeginInit();
            this.SuspendLayout();
            // 
            // txtSoTin
            // 
            this.txtSoTin.Location = new System.Drawing.Point(17, 82);
            this.txtSoTin.Name = "txtSoTin";
            this.txtSoTin.Size = new System.Drawing.Size(175, 20);
            this.txtSoTin.TabIndex = 27;
            // 
            // TxtTenMH
            // 
            this.TxtTenMH.Location = new System.Drawing.Point(224, 39);
            this.TxtTenMH.Name = "TxtTenMH";
            this.TxtTenMH.Size = new System.Drawing.Size(207, 20);
            this.TxtTenMH.TabIndex = 28;
            // 
            // txtMaMH
            // 
            this.txtMaMH.AcceptsReturn = true;
            this.txtMaMH.HideSelection = false;
            this.txtMaMH.Location = new System.Drawing.Point(17, 39);
            this.txtMaMH.Name = "txtMaMH";
            this.txtMaMH.Size = new System.Drawing.Size(175, 20);
            this.txtMaMH.TabIndex = 29;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(14, 66);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(36, 13);
            this.label3.TabIndex = 24;
            this.label3.Text = "Số tín";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(221, 23);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(70, 13);
            this.label2.TabIndex = 25;
            this.label2.Text = "Tên môn học";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(14, 23);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(66, 13);
            this.label4.TabIndex = 26;
            this.label4.Text = "Mã môn học";
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.txtSoTin);
            this.groupBox1.Controls.Add(this.pictureBox1);
            this.groupBox1.Controls.Add(this.label3);
            this.groupBox1.Controls.Add(this.label1);
            this.groupBox1.Controls.Add(this.btnSuatimkiem);
            this.groupBox1.Controls.Add(this.TxtTenMH);
            this.groupBox1.Controls.Add(this.btnThoattimkiem);
            this.groupBox1.Controls.Add(this.label2);
            this.groupBox1.Controls.Add(this.btnXoasuatimkiem);
            this.groupBox1.Controls.Add(this.txtMaMH);
            this.groupBox1.Controls.Add(this.label4);
            this.groupBox1.Location = new System.Drawing.Point(12, 251);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(468, 178);
            this.groupBox1.TabIndex = 23;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "Sửa thông tin";
            // 
            // btnSuatimkiem
            // 
            this.btnSuatimkiem.Location = new System.Drawing.Point(6, 120);
            this.btnSuatimkiem.Name = "btnSuatimkiem";
            this.btnSuatimkiem.Size = new System.Drawing.Size(80, 39);
            this.btnSuatimkiem.TabIndex = 0;
            this.btnSuatimkiem.Text = "Sửa";
            this.btnSuatimkiem.UseVisualStyleBackColor = true;
            this.btnSuatimkiem.Click += new System.EventHandler(this.btnSuatimkiem_Click);
            // 
            // btnThoattimkiem
            // 
            this.btnThoattimkiem.Location = new System.Drawing.Point(178, 120);
            this.btnThoattimkiem.Name = "btnThoattimkiem";
            this.btnThoattimkiem.Size = new System.Drawing.Size(80, 39);
            this.btnThoattimkiem.TabIndex = 8;
            this.btnThoattimkiem.Text = "Thoát";
            this.btnThoattimkiem.UseVisualStyleBackColor = true;
            this.btnThoattimkiem.Click += new System.EventHandler(this.btnThoattimkiem_Click);
            // 
            // btnXoasuatimkiem
            // 
            this.btnXoasuatimkiem.Location = new System.Drawing.Point(92, 120);
            this.btnXoasuatimkiem.Name = "btnXoasuatimkiem";
            this.btnXoasuatimkiem.Size = new System.Drawing.Size(80, 39);
            this.btnXoasuatimkiem.TabIndex = 1;
            this.btnXoasuatimkiem.Text = "Xoá";
            this.btnXoasuatimkiem.UseVisualStyleBackColor = true;
            this.btnXoasuatimkiem.Click += new System.EventHandler(this.btnXoasuatimkiem_Click);
            // 
            // pictureBox1
            // 
            this.pictureBox1.Image = ((System.Drawing.Image)(resources.GetObject("pictureBox1.Image")));
            this.pictureBox1.Location = new System.Drawing.Point(369, 65);
            this.pictureBox1.Name = "pictureBox1";
            this.pictureBox1.Size = new System.Drawing.Size(62, 36);
            this.pictureBox1.SizeMode = System.Windows.Forms.PictureBoxSizeMode.Zoom;
            this.pictureBox1.TabIndex = 22;
            this.pictureBox1.TabStop = false;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Microsoft YaHei", 15.75F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.ForeColor = System.Drawing.SystemColors.Highlight;
            this.label1.Location = new System.Drawing.Point(207, 66);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(156, 28);
            this.label1.TabIndex = 21;
            this.label1.Text = "Sửa thông tin";
            // 
            // dtgvMonHoc
            // 
            this.dtgvMonHoc.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dtgvMonHoc.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.Column1,
            this.Column2,
            this.Column3});
            this.dtgvMonHoc.Location = new System.Drawing.Point(12, 12);
            this.dtgvMonHoc.Name = "dtgvMonHoc";
            this.dtgvMonHoc.Size = new System.Drawing.Size(468, 233);
            this.dtgvMonHoc.TabIndex = 20;
            this.dtgvMonHoc.CellContentClick += new System.Windows.Forms.DataGridViewCellEventHandler(this.dtgvMonHoc_CellContentClick);
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
            // SuaMonHoc
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(507, 444);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.dtgvMonHoc);
            this.Name = "SuaMonHoc";
            this.Text = "SuaMonHoc";
            this.Load += new System.EventHandler(this.SuaMonHoc_Load);
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.dtgvMonHoc)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.TextBox txtSoTin;
        private System.Windows.Forms.TextBox TxtTenMH;
        public System.Windows.Forms.TextBox txtMaMH;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.Button btnSuatimkiem;
        private System.Windows.Forms.Button btnThoattimkiem;
        private System.Windows.Forms.Button btnXoasuatimkiem;
        private System.Windows.Forms.PictureBox pictureBox1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.DataGridView dtgvMonHoc;
        private System.Windows.Forms.DataGridViewTextBoxColumn Column1;
        private System.Windows.Forms.DataGridViewTextBoxColumn Column2;
        private System.Windows.Forms.DataGridViewTextBoxColumn Column3;
    }
}