﻿namespace Auxiliary_tool
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
            this.redrawChartButton = new Guna.UI2.WinForms.Guna2GradientButton();
            this.directSelectStudentBox = new Guna.UI2.WinForms.Guna2ComboBox();
            this.scoreFluctuationComboBox = new Guna.UI2.WinForms.Guna2ComboBox();
            this.displayDataLenthComboBox = new Guna.UI2.WinForms.Guna2ComboBox();
            this.label4 = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.panel2 = new System.Windows.Forms.Panel();
            this.panel3 = new System.Windows.Forms.Panel();
            this.panel4 = new System.Windows.Forms.Panel();
            this.panel5 = new System.Windows.Forms.Panel();
            this.panel1.SuspendLayout();
            this.panel2.SuspendLayout();
            this.panel3.SuspendLayout();
            this.panel4.SuspendLayout();
            this.panel5.SuspendLayout();
            this.SuspendLayout();
            // 
            // cartesianChart
            // 
            this.cartesianChart.Dock = System.Windows.Forms.DockStyle.Fill;
            this.cartesianChart.Location = new System.Drawing.Point(0, 0);
            this.cartesianChart.Name = "cartesianChart";
            this.cartesianChart.Size = new System.Drawing.Size(1051, 452);
            this.cartesianChart.TabIndex = 0;
            this.cartesianChart.Text = "cartesianChart1";
            // 
            // charttestButton
            // 
            this.charttestButton.DisabledState.BorderColor = System.Drawing.Color.DarkGray;
            this.charttestButton.DisabledState.CustomBorderColor = System.Drawing.Color.DarkGray;
            this.charttestButton.DisabledState.FillColor = System.Drawing.Color.FromArgb(((int)(((byte)(169)))), ((int)(((byte)(169)))), ((int)(((byte)(169)))));
            this.charttestButton.DisabledState.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(141)))), ((int)(((byte)(141)))), ((int)(((byte)(141)))));
            this.charttestButton.Font = new System.Drawing.Font("Century", 7F);
            this.charttestButton.ForeColor = System.Drawing.Color.White;
            this.charttestButton.Location = new System.Drawing.Point(15, 31);
            this.charttestButton.Name = "charttestButton";
            this.charttestButton.ShadowDecoration.Mode = Guna.UI2.WinForms.Enums.ShadowMode.Circle;
            this.charttestButton.Size = new System.Drawing.Size(66, 67);
            this.charttestButton.TabIndex = 3;
            this.charttestButton.Text = "Clear";
            this.charttestButton.Click += new System.EventHandler(this.charttestButton_Click);
            // 
            // panel1
            // 
            this.panel1.Controls.Add(this.panel5);
            this.panel1.Controls.Add(this.panel4);
            this.panel1.Controls.Add(this.panel3);
            this.panel1.Dock = System.Windows.Forms.DockStyle.Top;
            this.panel1.Location = new System.Drawing.Point(0, 0);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(1051, 121);
            this.panel1.TabIndex = 4;
            // 
            // redrawChartButton
            // 
            this.redrawChartButton.DisabledState.BorderColor = System.Drawing.Color.DarkGray;
            this.redrawChartButton.DisabledState.CustomBorderColor = System.Drawing.Color.DarkGray;
            this.redrawChartButton.DisabledState.FillColor = System.Drawing.Color.FromArgb(((int)(((byte)(169)))), ((int)(((byte)(169)))), ((int)(((byte)(169)))));
            this.redrawChartButton.DisabledState.FillColor2 = System.Drawing.Color.FromArgb(((int)(((byte)(169)))), ((int)(((byte)(169)))), ((int)(((byte)(169)))));
            this.redrawChartButton.DisabledState.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(141)))), ((int)(((byte)(141)))), ((int)(((byte)(141)))));
            this.redrawChartButton.FillColor = System.Drawing.Color.Orchid;
            this.redrawChartButton.FillColor2 = System.Drawing.Color.FromArgb(((int)(((byte)(57)))), ((int)(((byte)(197)))), ((int)(((byte)(187)))));
            this.redrawChartButton.Font = new System.Drawing.Font("幼圆", 10.8F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.redrawChartButton.ForeColor = System.Drawing.Color.White;
            this.redrawChartButton.Location = new System.Drawing.Point(446, 73);
            this.redrawChartButton.Name = "redrawChartButton";
            this.redrawChartButton.Size = new System.Drawing.Size(141, 39);
            this.redrawChartButton.TabIndex = 1;
            this.redrawChartButton.Text = "下一组数据";
            this.redrawChartButton.TextRenderingHint = System.Drawing.Text.TextRenderingHint.SingleBitPerPixelGridFit;
            this.redrawChartButton.Click += new System.EventHandler(this.RedrawChartButton_Click);
            // 
            // directSelectStudentBox
            // 
            this.directSelectStudentBox.BackColor = System.Drawing.Color.Silver;
            this.directSelectStudentBox.BorderThickness = 0;
            this.directSelectStudentBox.DrawMode = System.Windows.Forms.DrawMode.OwnerDrawFixed;
            this.directSelectStudentBox.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.directSelectStudentBox.FillColor = System.Drawing.SystemColors.Control;
            this.directSelectStudentBox.FocusedColor = System.Drawing.Color.White;
            this.directSelectStudentBox.FocusedState.BorderColor = System.Drawing.Color.White;
            this.directSelectStudentBox.Font = new System.Drawing.Font("Century Gothic", 11F, System.Drawing.FontStyle.Bold);
            this.directSelectStudentBox.ForeColor = System.Drawing.Color.FromArgb(((int)(((byte)(0)))), ((int)(((byte)(192)))), ((int)(((byte)(192)))));
            this.directSelectStudentBox.ItemHeight = 30;
            this.directSelectStudentBox.Location = new System.Drawing.Point(190, 21);
            this.directSelectStudentBox.MaxDropDownItems = 3;
            this.directSelectStudentBox.Name = "directSelectStudentBox";
            this.directSelectStudentBox.Size = new System.Drawing.Size(245, 36);
            this.directSelectStudentBox.TabIndex = 7;
            this.directSelectStudentBox.SelectedIndexChanged += new System.EventHandler(this.DirectSelectStudentComboBox_SelectedIndexChanged);
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
            this.scoreFluctuationComboBox.Location = new System.Drawing.Point(270, 73);
            this.scoreFluctuationComboBox.Name = "scoreFluctuationComboBox";
            this.scoreFluctuationComboBox.Size = new System.Drawing.Size(165, 36);
            this.scoreFluctuationComboBox.TabIndex = 7;
            this.scoreFluctuationComboBox.SelectedIndexChanged += new System.EventHandler(this.DirectSelectStudentComboBox_SelectedIndexChanged);
            // 
            // displayDataLenthComboBox
            // 
            this.displayDataLenthComboBox.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
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
            this.displayDataLenthComboBox.ForeColor = System.Drawing.Color.DimGray;
            this.displayDataLenthComboBox.ItemHeight = 30;
            this.displayDataLenthComboBox.Items.AddRange(new object[] {
            "All",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10"});
            this.displayDataLenthComboBox.ItemsAppearance.SelectedBackColor = System.Drawing.Color.White;
            this.displayDataLenthComboBox.Location = new System.Drawing.Point(223, 73);
            this.displayDataLenthComboBox.Name = "displayDataLenthComboBox";
            this.displayDataLenthComboBox.Size = new System.Drawing.Size(112, 36);
            this.displayDataLenthComboBox.TabIndex = 5;
            this.displayDataLenthComboBox.TextAlign = System.Windows.Forms.HorizontalAlignment.Center;
            this.displayDataLenthComboBox.SelectedIndexChanged += new System.EventHandler(this.displayDataLenthComboBox_SelectedIndexChanged);
            // 
            // label4
            // 
            this.label4.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.label4.AutoSize = true;
            this.label4.Font = new System.Drawing.Font("幼圆", 15F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.label4.ForeColor = System.Drawing.SystemColors.Highlight;
            this.label4.Location = new System.Drawing.Point(14, 31);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(147, 25);
            this.label4.TabIndex = 6;
            this.label4.Text = "直接选择：";
            // 
            // label3
            // 
            this.label3.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.label3.AutoSize = true;
            this.label3.Font = new System.Drawing.Font("幼圆", 15F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(134)));
            this.label3.ForeColor = System.Drawing.SystemColors.Highlight;
            this.label3.Location = new System.Drawing.Point(14, 79);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(188, 25);
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
            this.panel2.Size = new System.Drawing.Size(1051, 452);
            this.panel2.TabIndex = 5;
            // 
            // panel3
            // 
            this.panel3.Controls.Add(this.label1);
            this.panel3.Controls.Add(this.label2);
            this.panel3.Controls.Add(this.displayDataLenthComboBox);
            this.panel3.Dock = System.Windows.Forms.DockStyle.Left;
            this.panel3.Location = new System.Drawing.Point(0, 0);
            this.panel3.Name = "panel3";
            this.panel3.Size = new System.Drawing.Size(360, 121);
            this.panel3.TabIndex = 8;
            // 
            // panel4
            // 
            this.panel4.Controls.Add(this.charttestButton);
            this.panel4.Dock = System.Windows.Forms.DockStyle.Right;
            this.panel4.Location = new System.Drawing.Point(953, 0);
            this.panel4.Name = "panel4";
            this.panel4.Size = new System.Drawing.Size(98, 121);
            this.panel4.TabIndex = 9;
            // 
            // panel5
            // 
            this.panel5.Controls.Add(this.directSelectStudentBox);
            this.panel5.Controls.Add(this.redrawChartButton);
            this.panel5.Controls.Add(this.scoreFluctuationComboBox);
            this.panel5.Controls.Add(this.label4);
            this.panel5.Controls.Add(this.label3);
            this.panel5.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panel5.Location = new System.Drawing.Point(360, 0);
            this.panel5.Name = "panel5";
            this.panel5.Size = new System.Drawing.Size(593, 121);
            this.panel5.TabIndex = 10;
            // 
            // Score_Analysis_Panle
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.panel2);
            this.Controls.Add(this.panel1);
            this.Name = "Score_Analysis_Panle";
            this.Size = new System.Drawing.Size(1051, 573);
            this.Load += new System.EventHandler(this.Score_Analysis_Load);
            this.panel1.ResumeLayout(false);
            this.panel2.ResumeLayout(false);
            this.panel3.ResumeLayout(false);
            this.panel3.PerformLayout();
            this.panel4.ResumeLayout(false);
            this.panel5.ResumeLayout(false);
            this.panel5.PerformLayout();
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
        private Guna.UI2.WinForms.Guna2GradientButton redrawChartButton;
        private Guna.UI2.WinForms.Guna2ComboBox directSelectStudentBox;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.Panel panel5;
        private System.Windows.Forms.Panel panel4;
        private System.Windows.Forms.Panel panel3;
    }
}
