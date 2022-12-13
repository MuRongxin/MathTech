namespace Auxiliary_tool
{
    partial class Score_Analysis_Panle
    {
        /// <summary> 
        /// 必需的设计器变量。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary> 
        /// 清理所有正在使用的资源。
        /// </summary>
        /// <param name="disposing">如果应释放托管资源，为 true；否则为 false。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region 组件设计器生成的代码

        /// <summary> 
        /// 设计器支持所需的方法 - 不要修改
        /// 使用代码编辑器修改此方法的内容。
        /// </summary>
        private void InitializeComponent()
        {
            this.cartesianChart = new LiveCharts.WinForms.CartesianChart();
            this.charttestButton = new Guna.UI2.WinForms.Guna2CircleButton();
            this.panel1 = new System.Windows.Forms.Panel();
            this.scoreFluctuationComboBox = new Guna.UI2.WinForms.Guna2ComboBox();
            this.displayDataLenthComboBox = new Guna.UI2.WinForms.Guna2ComboBox();
            this.label3 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.panel2 = new System.Windows.Forms.Panel();
            this.panel1.SuspendLayout();
            this.panel2.SuspendLayout();
            this.SuspendLayout();
            // 
            // cartesianChart
            // 
            this.cartesianChart.Dock = System.Windows.Forms.DockStyle.Fill;
            this.cartesianChart.Location = new System.Drawing.Point(0, 0);
            this.cartesianChart.Name = "cartesianChart";
            this.cartesianChart.Size = new System.Drawing.Size(1023, 452);
            this.cartesianChart.TabIndex = 0;
            this.cartesianChart.Text = "cartesianChart1";
            // 
            // charttestButton
            // 
            this.charttestButton.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.charttestButton.DisabledState.BorderColor = System.Drawing.Color.DarkGray;
            this.charttestButton.DisabledState.CustomBorderColor = System.Drawing.Color.DarkGray;
            this.charttestButton.DisabledState.FillColor = System.Drawing.Color.FromArgb(((int)(((byte)(169)))), ((int)(((byte)(169)))), ((int)(((byte)(169)))));
            this.charttestButton.DisabledState.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(141)))), ((int)(((byte)(141)))), ((int)(((byte)(141)))));
            this.charttestButton.Font = new System.Drawing.Font("Segoe UI", 10F);
            this.charttestButton.ForeColor = System.Drawing.Color.White;
            this.charttestButton.Location = new System.Drawing.Point(897, 57);
            this.charttestButton.Name = "charttestButton";
            this.charttestButton.ShadowDecoration.Mode = Guna.UI2.WinForms.Enums.ShadowMode.Circle;
            this.charttestButton.Size = new System.Drawing.Size(59, 58);
            this.charttestButton.TabIndex = 3;
            this.charttestButton.Text = "Chart Value";
            this.charttestButton.Click += new System.EventHandler(this.charttestButton_Click);
            // 
            // panel1
            // 
            this.panel1.Controls.Add(this.scoreFluctuationComboBox);
            this.panel1.Controls.Add(this.displayDataLenthComboBox);
            this.panel1.Controls.Add(this.label3);
            this.panel1.Controls.Add(this.label2);
            this.panel1.Controls.Add(this.label1);
            this.panel1.Controls.Add(this.charttestButton);
            this.panel1.Dock = System.Windows.Forms.DockStyle.Top;
            this.panel1.Location = new System.Drawing.Point(0, 0);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(1023, 121);
            this.panel1.TabIndex = 4;
            // 
            // scoreFluctuationComboBox
            // 
            this.scoreFluctuationComboBox.BackColor = System.Drawing.Color.Silver;
            this.scoreFluctuationComboBox.BorderThickness = 0;
            this.scoreFluctuationComboBox.DrawMode = System.Windows.Forms.DrawMode.OwnerDrawFixed;
            this.scoreFluctuationComboBox.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.scoreFluctuationComboBox.FillColor = System.Drawing.SystemColors.Control;
            this.scoreFluctuationComboBox.FocusedColor = System.Drawing.Color.White;
            this.scoreFluctuationComboBox.FocusedState.BorderColor = System.Drawing.Color.White;
            this.scoreFluctuationComboBox.Font = new System.Drawing.Font("Century Gothic", 11F, System.Drawing.FontStyle.Bold);
            this.scoreFluctuationComboBox.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(192)))), ((int)(((byte)(192)))));
            this.scoreFluctuationComboBox.ItemHeight = 30;
            this.scoreFluctuationComboBox.Items.AddRange(new object[] {
            "0~0.2",
            "0.2~0.4",
            "0.4~1.0",
            "All"});
            this.scoreFluctuationComboBox.Location = new System.Drawing.Point(590, 73);
            this.scoreFluctuationComboBox.Name = "scoreFluctuationComboBox";
            this.scoreFluctuationComboBox.Size = new System.Drawing.Size(174, 36);
            this.scoreFluctuationComboBox.TabIndex = 7;
            this.scoreFluctuationComboBox.SelectedIndexChanged += new System.EventHandler(this.scoreFluctuationComboBox_SelectedIndexChanged);
            // 
            // displayDataLenthComboBox
            // 
            this.displayDataLenthComboBox.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.displayDataLenthComboBox.BackColor = System.Drawing.Color.Silver;
            this.displayDataLenthComboBox.BorderColor = System.Drawing.Color.White;
            this.displayDataLenthComboBox.BorderRadius = 1;
            this.displayDataLenthComboBox.BorderStyle = System.Drawing.Drawing2D.DashStyle.DashDot;
            this.displayDataLenthComboBox.DrawMode = System.Windows.Forms.DrawMode.OwnerDrawFixed;
            this.displayDataLenthComboBox.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.displayDataLenthComboBox.FillColor = System.Drawing.Color.WhiteSmoke;
            this.displayDataLenthComboBox.FocusedColor = System.Drawing.Color.White;
            this.displayDataLenthComboBox.FocusedState.BorderColor = System.Drawing.Color.White;
            this.displayDataLenthComboBox.Font = new System.Drawing.Font("Century Gothic", 12F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.displayDataLenthComboBox.ForeColor = System.Drawing.Color.Black;
            this.displayDataLenthComboBox.ItemHeight = 30;
            this.displayDataLenthComboBox.Items.AddRange(new object[] {
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "All"});
            this.displayDataLenthComboBox.ItemsAppearance.SelectedBackColor = System.Drawing.Color.White;
            this.displayDataLenthComboBox.Location = new System.Drawing.Point(211, 73);
            this.displayDataLenthComboBox.Name = "displayDataLenthComboBox";
            this.displayDataLenthComboBox.Size = new System.Drawing.Size(108, 36);
            this.displayDataLenthComboBox.TabIndex = 5;
            this.displayDataLenthComboBox.SelectedIndexChanged += new System.EventHandler(this.displayDataLenthComboBox_SelectedIndexChanged);
            // 
            // label3
            // 
            this.label3.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.label3.AutoSize = true;
            this.label3.Font = new System.Drawing.Font("幼圆", 13F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.label3.ForeColor = System.Drawing.SystemColors.Highlight;
            this.label3.Location = new System.Drawing.Point(395, 80);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(160, 22);
            this.label3.TabIndex = 6;
            this.label3.Text = "成绩波动范围:";
            // 
            // label2
            // 
            this.label2.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.label2.AutoSize = true;
            this.label2.Font = new System.Drawing.Font("幼圆", 13F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.label2.ForeColor = System.Drawing.SystemColors.Highlight;
            this.label2.Location = new System.Drawing.Point(19, 80);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(160, 22);
            this.label2.TabIndex = 6;
            this.label2.Text = "单次数据长度:";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.label1.Font = new System.Drawing.Font("Century Gothic", 16.2F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.ForeColor = System.Drawing.SystemColors.HotTrack;
            this.label1.Location = new System.Drawing.Point(15, 20);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(191, 34);
            this.label1.TabIndex = 4;
            this.label1.Text = "Data Filtering";
            // 
            // panel2
            // 
            this.panel2.Controls.Add(this.cartesianChart);
            this.panel2.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panel2.Location = new System.Drawing.Point(0, 121);
            this.panel2.Name = "panel2";
            this.panel2.Size = new System.Drawing.Size(1023, 452);
            this.panel2.TabIndex = 5;
            // 
            // Score_Analysis_Panle
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.panel2);
            this.Controls.Add(this.panel1);
            this.Name = "Score_Analysis_Panle";
            this.Size = new System.Drawing.Size(1023, 573);
            this.Load += new System.EventHandler(this.Score_Analysis_Load);
            this.panel1.ResumeLayout(false);
            this.panel1.PerformLayout();
            this.panel2.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion

        private LiveCharts.WinForms.CartesianChart cartesianChart;
        private Guna.UI2.WinForms.Guna2CircleButton charttestButton;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.Panel panel2;
        private System.Windows.Forms.Label label1;
        private Guna.UI2.WinForms.Guna2ComboBox displayDataLenthComboBox;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Label label3;
        private Guna.UI2.WinForms.Guna2ComboBox scoreFluctuationComboBox;
    }
}
