namespace WindowsFormsApp1
{
    partial class Doimatkau
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
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.txt_mkcu = new System.Windows.Forms.TextBox();
            this.txt_mkmoi = new System.Windows.Forms.TextBox();
            this.txt_xacnhan = new System.Windows.Forms.TextBox();
            this.label4 = new System.Windows.Forms.Label();
            this.btn_xacnhan = new System.Windows.Forms.Button();
            this.btn_huy = new System.Windows.Forms.Button();
            this.label5 = new System.Windows.Forms.Label();
            this.txt_TenDN = new System.Windows.Forms.TextBox();
            this.SuspendLayout();
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Rockwell", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.Location = new System.Drawing.Point(20, 90);
            this.label1.Margin = new System.Windows.Forms.Padding(2, 0, 2, 0);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(115, 16);
            this.label1.TabIndex = 0;
            this.label1.Text = "Nhập mật khẩu cũ";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("Rockwell", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label2.Location = new System.Drawing.Point(20, 118);
            this.label2.Margin = new System.Windows.Forms.Padding(2, 0, 2, 0);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(123, 16);
            this.label2.TabIndex = 1;
            this.label2.Text = "Nhập mật khẩu mới";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Font = new System.Drawing.Font("Rockwell", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label3.Location = new System.Drawing.Point(20, 146);
            this.label3.Margin = new System.Windows.Forms.Padding(2, 0, 2, 0);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(140, 16);
            this.label3.TabIndex = 2;
            this.label3.Text = "Nhập lại mật khẩu mới";
            // 
            // txt_mkcu
            // 
            this.txt_mkcu.Location = new System.Drawing.Point(169, 90);
            this.txt_mkcu.Margin = new System.Windows.Forms.Padding(2);
            this.txt_mkcu.Name = "txt_mkcu";
            this.txt_mkcu.Size = new System.Drawing.Size(174, 20);
            this.txt_mkcu.TabIndex = 3;
            // 
            // txt_mkmoi
            // 
            this.txt_mkmoi.Location = new System.Drawing.Point(169, 118);
            this.txt_mkmoi.Margin = new System.Windows.Forms.Padding(2);
            this.txt_mkmoi.Name = "txt_mkmoi";
            this.txt_mkmoi.Size = new System.Drawing.Size(174, 20);
            this.txt_mkmoi.TabIndex = 4;
            // 
            // txt_xacnhan
            // 
            this.txt_xacnhan.Location = new System.Drawing.Point(169, 142);
            this.txt_xacnhan.Margin = new System.Windows.Forms.Padding(2);
            this.txt_xacnhan.Name = "txt_xacnhan";
            this.txt_xacnhan.Size = new System.Drawing.Size(174, 20);
            this.txt_xacnhan.TabIndex = 5;
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Font = new System.Drawing.Font("Consolas", 14.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label4.Location = new System.Drawing.Point(173, 19);
            this.label4.Margin = new System.Windows.Forms.Padding(2, 0, 2, 0);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(130, 22);
            this.label4.TabIndex = 6;
            this.label4.Text = "ĐỔI MẬT KHẨU";
            this.label4.Click += new System.EventHandler(this.label4_Click);
            // 
            // btn_xacnhan
            // 
            this.btn_xacnhan.Font = new System.Drawing.Font("Rockwell", 9.75F);
            this.btn_xacnhan.Location = new System.Drawing.Point(87, 183);
            this.btn_xacnhan.Margin = new System.Windows.Forms.Padding(2);
            this.btn_xacnhan.Name = "btn_xacnhan";
            this.btn_xacnhan.Size = new System.Drawing.Size(83, 37);
            this.btn_xacnhan.TabIndex = 7;
            this.btn_xacnhan.Text = "Xác nhận";
            this.btn_xacnhan.UseVisualStyleBackColor = true;
            this.btn_xacnhan.Click += new System.EventHandler(this.btn_xacnhan_Click);
            // 
            // btn_huy
            // 
            this.btn_huy.Font = new System.Drawing.Font("Rockwell", 9.75F);
            this.btn_huy.Location = new System.Drawing.Point(235, 183);
            this.btn_huy.Margin = new System.Windows.Forms.Padding(2);
            this.btn_huy.Name = "btn_huy";
            this.btn_huy.Size = new System.Drawing.Size(83, 37);
            this.btn_huy.TabIndex = 8;
            this.btn_huy.Text = "Huỷ";
            this.btn_huy.UseVisualStyleBackColor = true;
            this.btn_huy.Click += new System.EventHandler(this.btn_huy_Click);
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Font = new System.Drawing.Font("Rockwell", 9.75F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label5.Location = new System.Drawing.Point(20, 61);
            this.label5.Margin = new System.Windows.Forms.Padding(2, 0, 2, 0);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(96, 16);
            this.label5.TabIndex = 9;
            this.label5.Text = "Tên đăng nhập";
            // 
            // txt_TenDN
            // 
            this.txt_TenDN.Location = new System.Drawing.Point(169, 61);
            this.txt_TenDN.Margin = new System.Windows.Forms.Padding(2);
            this.txt_TenDN.Name = "txt_TenDN";
            this.txt_TenDN.Size = new System.Drawing.Size(174, 20);
            this.txt_TenDN.TabIndex = 10;
            // 
            // Doimatkau
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.LightSteelBlue;
            this.ClientSize = new System.Drawing.Size(482, 231);
            this.Controls.Add(this.txt_TenDN);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.btn_huy);
            this.Controls.Add(this.btn_xacnhan);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.txt_xacnhan);
            this.Controls.Add(this.txt_mkmoi);
            this.Controls.Add(this.txt_mkcu);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.label1);
            this.Margin = new System.Windows.Forms.Padding(2);
            this.Name = "Doimatkau";
            this.Text = "Doimatkau";
            this.Load += new System.EventHandler(this.Doimatkau_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox txt_mkcu;
        private System.Windows.Forms.TextBox txt_mkmoi;
        private System.Windows.Forms.TextBox txt_xacnhan;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Button btn_xacnhan;
        private System.Windows.Forms.Button btn_huy;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.TextBox txt_TenDN;
    }
}