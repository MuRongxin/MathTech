namespace 图表工具
{
    partial class DataManager
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
            this.splitContainer1 = new System.Windows.Forms.SplitContainer();
            this.columnGrid = new System.Windows.Forms.DataGridView();
            this.ColumnIndex = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.ColumnName = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.reportGrid = new System.Windows.Forms.DataGridView();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.数据管理ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.备份ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.清空ToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).BeginInit();
            this.splitContainer1.Panel1.SuspendLayout();
            this.splitContainer1.Panel2.SuspendLayout();
            this.splitContainer1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.columnGrid)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.reportGrid)).BeginInit();
            this.menuStrip1.SuspendLayout();
            this.SuspendLayout();
            // 
            // splitContainer1
            // 
            this.splitContainer1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.splitContainer1.Location = new System.Drawing.Point(0, 25);
            this.splitContainer1.Name = "splitContainer1";
            // 
            // splitContainer1.Panel1
            // 
            this.splitContainer1.Panel1.Controls.Add(this.columnGrid);
            // 
            // splitContainer1.Panel2
            // 
            this.splitContainer1.Panel2.Controls.Add(this.reportGrid);
            this.splitContainer1.Size = new System.Drawing.Size(978, 505);
            this.splitContainer1.SplitterDistance = 263;
            this.splitContainer1.TabIndex = 0;
            // 
            // columnGrid
            // 
            this.columnGrid.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.columnGrid.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.ColumnIndex,
            this.ColumnName});
            this.columnGrid.Dock = System.Windows.Forms.DockStyle.Fill;
            this.columnGrid.Location = new System.Drawing.Point(0, 0);
            this.columnGrid.Name = "columnGrid";
            this.columnGrid.RowTemplate.Height = 23;
            this.columnGrid.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.columnGrid.Size = new System.Drawing.Size(263, 505);
            this.columnGrid.TabIndex = 0;
            this.columnGrid.CellBeginEdit += new System.Windows.Forms.DataGridViewCellCancelEventHandler(this.columnGrid_CellBeginEdit);
            this.columnGrid.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.columnGrid_CellEndEdit);
            this.columnGrid.UserAddedRow += new System.Windows.Forms.DataGridViewRowEventHandler(this.columnGrid_UserAddedRow);
            this.columnGrid.UserDeletedRow += new System.Windows.Forms.DataGridViewRowEventHandler(this.columnGrid_UserDeletedRow);
            // 
            // ColumnIndex
            // 
            this.ColumnIndex.HeaderText = "序号";
            this.ColumnIndex.Name = "ColumnIndex";
            this.ColumnIndex.ReadOnly = true;
            // 
            // ColumnName
            // 
            this.ColumnName.HeaderText = "列名称";
            this.ColumnName.Name = "ColumnName";
            // 
            // reportGrid
            // 
            this.reportGrid.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.reportGrid.Dock = System.Windows.Forms.DockStyle.Fill;
            this.reportGrid.Location = new System.Drawing.Point(0, 0);
            this.reportGrid.Name = "reportGrid";
            this.reportGrid.RowTemplate.Height = 23;
            this.reportGrid.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.reportGrid.Size = new System.Drawing.Size(711, 505);
            this.reportGrid.TabIndex = 0;
            this.reportGrid.CellBeginEdit += new System.Windows.Forms.DataGridViewCellCancelEventHandler(this.reportGrid_CellBeginEdit);
            this.reportGrid.CellEndEdit += new System.Windows.Forms.DataGridViewCellEventHandler(this.reportGrid_CellEndEdit);
            this.reportGrid.UserAddedRow += new System.Windows.Forms.DataGridViewRowEventHandler(this.reportGrid_UserAddedRow);
            this.reportGrid.UserDeletedRow += new System.Windows.Forms.DataGridViewRowEventHandler(this.reportGrid_UserDeletedRow);
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.数据管理ToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(978, 25);
            this.menuStrip1.TabIndex = 1;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // 数据管理ToolStripMenuItem
            // 
            this.数据管理ToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.备份ToolStripMenuItem,
            this.清空ToolStripMenuItem});
            this.数据管理ToolStripMenuItem.Name = "数据管理ToolStripMenuItem";
            this.数据管理ToolStripMenuItem.Size = new System.Drawing.Size(68, 21);
            this.数据管理ToolStripMenuItem.Text = "数据管理";
            // 
            // 备份ToolStripMenuItem
            // 
            this.备份ToolStripMenuItem.Name = "备份ToolStripMenuItem";
            this.备份ToolStripMenuItem.Size = new System.Drawing.Size(180, 22);
            this.备份ToolStripMenuItem.Text = "备份";
            this.备份ToolStripMenuItem.Click += new System.EventHandler(this.备份ToolStripMenuItem_Click);
            // 
            // 清空ToolStripMenuItem
            // 
            this.清空ToolStripMenuItem.Name = "清空ToolStripMenuItem";
            this.清空ToolStripMenuItem.Size = new System.Drawing.Size(180, 22);
            this.清空ToolStripMenuItem.Text = "清空";
            this.清空ToolStripMenuItem.Click += new System.EventHandler(this.清空ToolStripMenuItem_Click);
            // 
            // DataManager
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(978, 530);
            this.Controls.Add(this.splitContainer1);
            this.Controls.Add(this.menuStrip1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "DataManager";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "数据维护";
            this.FormClosing += new System.Windows.Forms.FormClosingEventHandler(this.DataManager_FormClosing);
            this.Load += new System.EventHandler(this.DataManager_Load);
            this.splitContainer1.Panel1.ResumeLayout(false);
            this.splitContainer1.Panel2.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.splitContainer1)).EndInit();
            this.splitContainer1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.columnGrid)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.reportGrid)).EndInit();
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.SplitContainer splitContainer1;
        private System.Windows.Forms.DataGridView columnGrid;
        private System.Windows.Forms.DataGridView reportGrid;
        private System.Windows.Forms.DataGridViewTextBoxColumn ColumnIndex;
        private System.Windows.Forms.DataGridViewTextBoxColumn ColumnName;
        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.ToolStripMenuItem 数据管理ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 备份ToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem 清空ToolStripMenuItem;
    }
}