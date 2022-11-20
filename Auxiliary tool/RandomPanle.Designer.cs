namespace Auxiliary_tool
{
    partial class RandomPanle
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
            this.components = new System.ComponentModel.Container();
            this.randomTimer = new System.Windows.Forms.Timer(this.components);
            this.panel1 = new System.Windows.Forms.Panel();
            this.panel4 = new System.Windows.Forms.Panel();
            this.radioButton2 = new System.Windows.Forms.RadioButton();
            this.radioButton1 = new System.Windows.Forms.RadioButton();
            this.label1 = new System.Windows.Forms.Label();
            this.resoultLabel = new System.Windows.Forms.Label();
            this.panel3 = new System.Windows.Forms.Panel();
            this.panel2 = new System.Windows.Forms.Panel();
            this.startRandomButton = new System.Windows.Forms.Button();
            this.panel5 = new System.Windows.Forms.Panel();
            this.changeColortimer = new System.Windows.Forms.Timer(this.components);
            this.panel1.SuspendLayout();
            this.panel4.SuspendLayout();
            this.panel2.SuspendLayout();
            this.SuspendLayout();
            // 
            // randomTimer
            // 
            this.randomTimer.Tick += new System.EventHandler(this.randomTimer_Tick);
            // 
            // panel1
            // 
            this.panel1.Controls.Add(this.panel4);
            this.panel1.Controls.Add(this.panel3);
            this.panel1.Dock = System.Windows.Forms.DockStyle.Top;
            this.panel1.Location = new System.Drawing.Point(0, 0);
            this.panel1.Name = "panel1";
            this.panel1.Size = new System.Drawing.Size(909, 315);
            this.panel1.TabIndex = 2;
            // 
            // panel4
            // 
            this.panel4.BackColor = System.Drawing.Color.Transparent;
            this.panel4.Controls.Add(this.resoultLabel);
            this.panel4.Controls.Add(this.radioButton2);
            this.panel4.Controls.Add(this.radioButton1);
            this.panel4.Controls.Add(this.label1);
            this.panel4.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panel4.Location = new System.Drawing.Point(125, 0);
            this.panel4.Name = "panel4";
            this.panel4.Size = new System.Drawing.Size(784, 315);
            this.panel4.TabIndex = 3;
            // 
            // radioButton2
            // 
            this.radioButton2.AutoSize = true;
            this.radioButton2.Font = new System.Drawing.Font("Californian FB", 15F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.radioButton2.Location = new System.Drawing.Point(311, 276);
            this.radioButton2.Name = "radioButton2";
            this.radioButton2.Size = new System.Drawing.Size(68, 33);
            this.radioButton2.TabIndex = 5;
            this.radioButton2.Text = "145";
            this.radioButton2.UseVisualStyleBackColor = true;
            this.radioButton2.CheckedChanged += new System.EventHandler(this.radioButton2_CheckedChanged);
            // 
            // radioButton1
            // 
            this.radioButton1.AutoSize = true;
            this.radioButton1.Checked = true;
            this.radioButton1.Font = new System.Drawing.Font("Californian FB", 15F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.radioButton1.Location = new System.Drawing.Point(199, 276);
            this.radioButton1.Name = "radioButton1";
            this.radioButton1.Size = new System.Drawing.Size(68, 33);
            this.radioButton1.TabIndex = 4;
            this.radioButton1.TabStop = true;
            this.radioButton1.Text = "143";
            this.radioButton1.UseVisualStyleBackColor = true;
            this.radioButton1.CheckedChanged += new System.EventHandler(this.radioButton1_CheckedChanged);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Font = new System.Drawing.Font("Trebuchet MS", 16.2F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.label1.Location = new System.Drawing.Point(11, 273);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(160, 36);
            this.label1.TabIndex = 3;
            this.label1.Text = "当前班级：";
            // 
            // resoultLabel
            // 
            this.resoultLabel.AutoSize = true;
            this.resoultLabel.Font = new System.Drawing.Font("黑体", 21F, System.Drawing.FontStyle.Bold);
            this.resoultLabel.Location = new System.Drawing.Point(39, 56);
            this.resoultLabel.Name = "resoultLabel";
            this.resoultLabel.Size = new System.Drawing.Size(631, 35);
            this.resoultLabel.TabIndex = 2;
            this.resoultLabel.Text = "Hi~ o(*￣▽￣*)ブ  你准备好了吗？";
            // 
            // panel3
            // 
            this.panel3.BackColor = System.Drawing.Color.Transparent;
            this.panel3.Dock = System.Windows.Forms.DockStyle.Left;
            this.panel3.Location = new System.Drawing.Point(0, 0);
            this.panel3.Name = "panel3";
            this.panel3.Size = new System.Drawing.Size(125, 315);
            this.panel3.TabIndex = 2;
            // 
            // panel2
            // 
            this.panel2.BackColor = System.Drawing.Color.Transparent;
            this.panel2.Controls.Add(this.startRandomButton);
            this.panel2.Dock = System.Windows.Forms.DockStyle.Right;
            this.panel2.Location = new System.Drawing.Point(417, 315);
            this.panel2.Name = "panel2";
            this.panel2.Size = new System.Drawing.Size(492, 278);
            this.panel2.TabIndex = 3;
            // 
            // startRandomButton
            // 
            this.startRandomButton.Font = new System.Drawing.Font("Californian FB", 15F, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, ((byte)(0)));
            this.startRandomButton.Location = new System.Drawing.Point(129, 96);
            this.startRandomButton.Name = "startRandomButton";
            this.startRandomButton.Size = new System.Drawing.Size(242, 54);
            this.startRandomButton.TabIndex = 1;
            this.startRandomButton.Text = "Start Random";
            this.startRandomButton.UseVisualStyleBackColor = true;
            this.startRandomButton.Click += new System.EventHandler(this.startRandomButton_Click);
            // 
            // panel5
            // 
            this.panel5.BackColor = System.Drawing.Color.Transparent;
            this.panel5.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panel5.Location = new System.Drawing.Point(0, 315);
            this.panel5.Name = "panel5";
            this.panel5.Size = new System.Drawing.Size(417, 278);
            this.panel5.TabIndex = 4;
            // 
            // changeColortimer
            // 
            this.changeColortimer.Interval = 10;
            this.changeColortimer.Tick += new System.EventHandler(this.changeColortimer_Tick);
            // 
            // RandomPanle
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(8F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.panel5);
            this.Controls.Add(this.panel2);
            this.Controls.Add(this.panel1);
            this.Name = "RandomPanle";
            this.Size = new System.Drawing.Size(909, 593);
            this.Load += new System.EventHandler(this.RandomPanle_Load);
            this.panel1.ResumeLayout(false);
            this.panel4.ResumeLayout(false);
            this.panel4.PerformLayout();
            this.panel2.ResumeLayout(false);
            this.ResumeLayout(false);

        }

        #endregion
        private System.Windows.Forms.Timer randomTimer;
        private System.Windows.Forms.Panel panel1;
        private System.Windows.Forms.Panel panel4;
        private System.Windows.Forms.Panel panel3;
        private System.Windows.Forms.Panel panel2;
        private System.Windows.Forms.Panel panel5;
        private System.Windows.Forms.Label resoultLabel;
        private System.Windows.Forms.Button startRandomButton;
        private System.Windows.Forms.RadioButton radioButton2;
        private System.Windows.Forms.RadioButton radioButton1;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Timer changeColortimer;
    }
}
