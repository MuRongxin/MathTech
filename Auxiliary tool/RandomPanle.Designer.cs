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
            this.panel2 = new System.Windows.Forms.Panel();
            this.panel3 = new System.Windows.Forms.Panel();
            this.panel4 = new System.Windows.Forms.Panel();
            this.panel5 = new System.Windows.Forms.Panel();
            this.resoultLabel = new System.Windows.Forms.Label();
            this.startRandomButton = new System.Windows.Forms.Button();
            this.panel1.SuspendLayout();
            this.panel2.SuspendLayout();
            this.panel4.SuspendLayout();
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
            // panel3
            // 
            this.panel3.BackColor = System.Drawing.Color.Transparent;
            this.panel3.Dock = System.Windows.Forms.DockStyle.Left;
            this.panel3.Location = new System.Drawing.Point(0, 0);
            this.panel3.Name = "panel3";
            this.panel3.Size = new System.Drawing.Size(120, 315);
            this.panel3.TabIndex = 2;
            // 
            // panel4
            // 
            this.panel4.BackColor = System.Drawing.Color.Transparent;
            this.panel4.Controls.Add(this.resoultLabel);
            this.panel4.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panel4.Location = new System.Drawing.Point(120, 0);
            this.panel4.Name = "panel4";
            this.panel4.Size = new System.Drawing.Size(789, 315);
            this.panel4.TabIndex = 3;
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
            // resoultLabel
            // 
            this.resoultLabel.AutoSize = true;
            this.resoultLabel.Font = new System.Drawing.Font("黑体", 22.2F, System.Drawing.FontStyle.Bold);
            this.resoultLabel.Location = new System.Drawing.Point(-123, 153);
            this.resoultLabel.Name = "resoultLabel";
            this.resoultLabel.Size = new System.Drawing.Size(666, 37);
            this.resoultLabel.TabIndex = 2;
            this.resoultLabel.Text = "Hi~ o(*￣▽￣*)ブ  你准备好了吗？";
            // 
            // startRandomButton
            // 
            this.startRandomButton.Location = new System.Drawing.Point(221, 86);
            this.startRandomButton.Name = "startRandomButton";
            this.startRandomButton.Size = new System.Drawing.Size(172, 54);
            this.startRandomButton.TabIndex = 1;
            this.startRandomButton.Text = "Start Random";
            this.startRandomButton.UseVisualStyleBackColor = true;
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
            this.panel2.ResumeLayout(false);
            this.panel4.ResumeLayout(false);
            this.panel4.PerformLayout();
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
    }
}
