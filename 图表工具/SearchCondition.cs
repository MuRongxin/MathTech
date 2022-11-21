using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using 图表工具.LocalData;

namespace 图表工具
{
    public partial class SearchCondition : Form
    {
        public SearchCondition()
        {
            InitializeComponent();
        }

        private void SearchCondition_Load(object sender, EventArgs e)
        {
            LoadGrid();
        }

        private void LoadGrid()
        {
            grid.Rows.Clear();

            grid.Rows.Add();
            grid.Rows[0].Cells["选择"].Value = Global.ColumnNameList.Count == ReportData.Columns.Count;
            grid.Rows[0].Cells["名称"].Value = "全选";

            for (int i = 0; i < ReportData.Columns.Count; i++)
            {
                grid.Rows.Add();

                grid.Rows[grid.Rows.Count - 1].Cells["选择"].Value = Global.ColumnNameList.Exists(c => c == ReportData.Columns[i].ColumnName);
                grid.Rows[grid.Rows.Count - 1].Cells["名称"].Value = ReportData.Columns[i].ColumnName;
            }
        }

        private void grid_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            bool isChecked = Convert.ToBoolean(grid.Rows[e.RowIndex].Cells[0].Value);
            //更改当前行
            grid.Rows[e.RowIndex].Cells[0].Value = !isChecked;

            string _name = grid.Rows[e.RowIndex].Cells["名称"].Value.ToString();

            if (_name == "全选")
            {
                for (int i = 0; i < grid.Rows.Count; i++)
                {
                    grid.Rows[i].Cells[0].Value = !isChecked;
                }

                Global.ColumnNameList.Clear();
                if (!isChecked == true)
                {
                    for (int i = 0; i < ReportData.Columns.Count; i++)
                    {
                        Global.ColumnNameList.Add(ReportData.Columns[i].ColumnName);
                    }
                }
            }
            else 
            {
                if (isChecked)
                {
                    //原来是选中 则取消选择
                    Global.ColumnNameList.Remove(_name);
                    grid.Rows[0].Cells["选择"].Value = false;
                }
                else
                {
                    //原来未选中 现在选中
                    Global.ColumnNameList.Add(_name);
                    if (Global.ColumnNameList.Count == ReportData.Columns.Count)
                    {
                        grid.Rows[0].Cells["选择"].Value = true;
                    }
                }
            }
        }
    }
}
