using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using 图表工具.LocalData;

namespace 图表工具
{
    public partial class DataManager : Form
    {
        public DataManager()
        {
            InitializeComponent();
        }

        private void DataManager_Load(object sender, EventArgs e)
        {
            LoadColumnGrid();
            LoadReportGrid();
        }

        private void LoadReportGrid()
        {
            var _columns = ReportData.Columns;

            reportGrid.Columns.Clear();
            reportGrid.Columns.Add(new DataGridViewTextBoxColumn()
            {
                Name = "ID",
                HeaderText = "ID",
                Visible = false
            });
            reportGrid.Columns.Add(new DataGridViewTextBoxColumn()
            {
                Name = "时间",
                HeaderText = "时间"
            });
            for (int i = 0; i < _columns.Count; i++)
            {
                reportGrid.Columns.Add(new DataGridViewTextBoxColumn()
                {
                    Name = _columns[i].ColumnName,
                    HeaderText = _columns[i].ColumnName
                });
            }


            reportGrid.Rows.Clear();
            for (int i = 0; i < ReportData.ResportDatas.Count; i++)
            {
                reportGrid.Rows.Add();
                reportGrid.Rows[reportGrid.Rows.Count - 2].Cells["ID"].Value = ReportData.ResportDatas[i].Id;
                reportGrid.Rows[reportGrid.Rows.Count - 2].Cells["时间"].Value = ReportData.ResportDatas[i].ReportDate.ToString("yyyy年MM月dd日");
                for (int j = 0; j < ReportData.ResportDatas[i].Columns.Count; j++)
                {
                    reportGrid.Rows[reportGrid.Rows.Count - 2].Cells[ReportData.ResportDatas[i].Columns[j].ColumnName].Value = ReportData.ResportDatas[i].Columns[j].ColumnValue;
                }
            }
        }

        private void LoadColumnGrid()
        {
            var _list = ReportData.Columns;
            columnGrid.Rows.Clear();
            for (int i = 0; i < _list.Count; i++)
            {
                columnGrid.Rows.Add();
                columnGrid.Rows[columnGrid.Rows.Count - 2].Cells["ColumnIndex"].Value = i + 1;
                columnGrid.Rows[columnGrid.Rows.Count - 2].Cells["ColumnName"].Value = _list[i].ColumnName;
            }
        }

        #region Column Grid Event

        bool newColumnRow = false;

        private void columnGrid_UserAddedRow(object sender, DataGridViewRowEventArgs e)
        {
            columnGrid.Rows[e.Row.Index - 1].Cells["ColumnIndex"].Value = columnGrid.Rows.Count - 1;
            newColumnRow = true;
        }

        private void columnGrid_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            if (columnGrid.Rows[e.RowIndex].Cells["ColumnName"].Value == null) return;
            if (newColumnRow)
            {
                //添加
                string _name = columnGrid.Rows[e.RowIndex].Cells["ColumnName"].Value.ToString();
                if (string.IsNullOrEmpty(_name))
                {
                    columnGrid.Rows.RemoveAt(e.RowIndex);
                    return;
                }
                ReportData.AddColumn(_name);
            }
            else
            {
                //编辑
                string _name = columnGrid.Rows[e.RowIndex].Cells["ColumnName"].Value.ToString();
                if (_name == columnEditValue) return;
                if (string.IsNullOrEmpty(_name))
                {
                    columnGrid.Rows.RemoveAt(e.RowIndex);
                    return;
                }
                ReportData.UpdateColumn(columnEditValue, _name);
            }
            newColumnRow = false;
            LoadReportGrid();
        }

        string columnEditValue = "";

        private void columnGrid_CellBeginEdit(object sender, DataGridViewCellCancelEventArgs e)
        {
            if (columnGrid.Rows[e.RowIndex].Cells["ColumnName"].Value == null) return;
            if (!newColumnRow)
            {
                columnEditValue = columnGrid.Rows[e.RowIndex].Cells["ColumnName"].Value.ToString();
            }
            else
            {
                columnEditValue = "";
            }
        }

        private void columnGrid_UserDeletedRow(object sender, DataGridViewRowEventArgs e)
        {
            string _name = e.Row.Cells[1].Value.ToString();
            if (string.IsNullOrEmpty(_name))
            {
                return;
            }
            ReportData.RemoveColumn(_name);
            for (int i = 0; i < columnGrid.Rows.Count - 1; i++)
            {
                columnGrid.Rows[i].Cells["ColumnIndex"].Value = i + 1;
            }
            LoadReportGrid();
        }


        #endregion

        #region Report Grid Event

        private void reportGrid_CellEndEdit(object sender, DataGridViewCellEventArgs e)
        {
            //当前编辑的列名称
            string currEditReportColumnName = reportGrid.Columns[e.ColumnIndex].Name;

            if (newReportRow)
            {
                string id = Guid.NewGuid().ToString();

                if (currEditReportColumnName == "时间")
                {
                    string dateStr = reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value.ToString();
                    DateTime date = DateTime.Now;
                    bool succeed = DateTime.TryParse(dateStr, out date);
                    if (!succeed)
                    {
                        MessageBox.Show("时间格式不正确");
                        reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value = currEditReportValue;
                        return;
                    }

                    //添加
                    ReportData.Add(new Models.ResportDataModel()
                    {
                        Id = id,
                        Columns = ReportData.Columns,
                        ReportDate = date
                    });
                }
                else
                {
                    var columns = ReportData.Columns;
                    for (int i = 0; i < columns.Count; i++)
                    {
                        if (columns[i].ColumnName == currEditReportColumnName)
                        {
                            try
                            {
                                columns[i].ColumnValue = Convert.ToDouble(reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value);
                            }
                            catch
                            {
                                MessageBox.Show("输入数字格式不正确");
                                reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value = currEditReportValue;
                                return;
                            }
                        }
                        else
                        {
                            columns[i].ColumnValue = 0;
                        }
                    }

                    //添加
                    ReportData.Add(new Models.ResportDataModel()
                    {
                        Id = id,
                        Columns = columns
                    });
                }

                reportGrid.Rows[e.RowIndex].Cells["ID"].Value = id;
            }
            else
            {
                string id = reportGrid.Rows[e.RowIndex].Cells["ID"].Value.ToString();
                //编辑
                if (currEditReportColumnName == "时间")
                {
                    DateTime date = DateTime.Now;
                    string dateStr = reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value.ToString();
                    bool succeed = DateTime.TryParse(dateStr, out date);
                    if (!succeed)
                    {
                        MessageBox.Show("时间格式不正确");
                        reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value = currEditReportValue;
                        return;
                    }
                    ReportData.UpdateDate(id, date);
                }
                else
                {
                    double _num = 0;
                    bool succeed = double.TryParse(reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value.ToString(), out _num);
                    if (!succeed)
                    {
                        MessageBox.Show("输入数字格式不正确");
                        reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value = currEditReportValue;
                        return;
                    }
                    ReportData.UpdateColumnValue(id, currEditReportColumnName, _num);
                }
            }

            newReportRow = false;
        }

        bool newReportRow = false;

        private void reportGrid_UserAddedRow(object sender, DataGridViewRowEventArgs e)
        {
            newReportRow = true;
        }

        string currEditReportValue = "";

        private void reportGrid_CellBeginEdit(object sender, DataGridViewCellCancelEventArgs e)
        {
            try
            {
                if (reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value == null) return;
                if (!newReportRow)
                {
                    currEditReportValue = reportGrid.Rows[e.RowIndex].Cells[e.ColumnIndex].Value.ToString();
                }
                else
                {
                    currEditReportValue = "";
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        #endregion

        private void DataManager_FormClosing(object sender, FormClosingEventArgs e)
        {
            Global.MainCharts.UpdateDataContext();

            Global.ColumnNameList.Clear();
            for (int i = 0; i < ReportData.Columns.Count; i++)
            {
                Global.ColumnNameList.Add(ReportData.Columns[i].ColumnName);
            }
        }

        private void reportGrid_UserDeletedRow(object sender, DataGridViewRowEventArgs e)
        {
            if (e.Row.Cells[0].Value == null) return;
            string _id = e.Row.Cells[0].Value.ToString();
            if (string.IsNullOrEmpty(_id))
            {
                return;
            }
            ReportData.RemoveData(_id);
            LoadReportGrid();
        }

        private void 清空ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string filePath = $"{AppDomain.CurrentDomain.BaseDirectory}data\\reportData.json";
            if (File.Exists(filePath))
            {
                File.Delete(filePath);
            }

            ReportData.Read();

            LoadColumnGrid();
            LoadReportGrid();

            MessageBox.Show("清空成功");
        }

        private void 备份ToolStripMenuItem_Click(object sender, EventArgs e)
        {
            string filePath = $"{AppDomain.CurrentDomain.BaseDirectory}data\\reportData.json";
            if (File.Exists(filePath))
            {
                File.Copy(filePath, $"{AppDomain.CurrentDomain.BaseDirectory}data\\reportData-{DateTime.Now.ToString("yyyyMMddhhmmss")}.json");
            }
            MessageBox.Show("备份成功");
        }
    }
}
