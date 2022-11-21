using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;
using 图表工具.LocalData;

namespace 图表工具
{
    /// <summary>
    /// CheckExcelData.xaml 的交互逻辑
    /// </summary>
    public partial class CheckExcelData : Window
    {
        public CheckExcelData()
        {
            InitializeComponent();
        }
        public static string excelPth = $"{AppDomain.CurrentDomain.BaseDirectory}data\\chat1.xlsx";

        private void Button_Click(object sender, RoutedEventArgs e)
        {
            IWorkbook wk = null;

            try
            {
                using (FileStream fs = new FileStream(excelPth, FileMode.Open, FileAccess.ReadWrite))
                {
                    wk = new XSSFWorkbook(fs);
                }
            }
            catch(Exception ex)
            {
                MessageBox.Show($"请检查[{System.IO.Path.GetFileName(excelPth)}]文档是否被打开,请关闭后重试");
                return;
            }

            ISheet sheet = wk.GetSheetAt(0);

            ReportData.ResportDatas.Clear();

            for (int i = 1; i < 35; i++)
            {
                Models.ResportDataModel model = new Models.ResportDataModel();

                DateTime time = sheet.GetRow(i).Cells[0].DateCellValue;
                double c1 = sheet.GetRow(i).Cells[1].NumericCellValue;
                double c2 = sheet.GetRow(i).Cells[2].NumericCellValue;
                double c3 = sheet.GetRow(i).Cells[3].NumericCellValue;

                //if (time.IndexOf("年") > 0) 
                //{
                //    time = time.Replace('年','-');
                //    time = time.Replace('月','-');
                //    time = time.Replace('日', '-');
                //    time = $"{time}T00:00:00";
                //}

                model.Id = Guid.NewGuid().ToString();
                model.ReportDate = time ;
                model.Columns = new List<Models.ColumnModel>()
                {
                    new Models.ColumnModel()
                    {
                        ColumnName="基金净多头",
                        ColumnValue=c1
                    },

                    new Models.ColumnModel()
                    {
                        ColumnName="布伦特原油价格",
                        ColumnValue=c2
                    },

                    new Models.ColumnModel()
                    {
                        ColumnName="成交量",
                        ColumnValue=c3
                    },
                };

                ReportData.ResportDatas.Add(model);
            }

            ReportData.Save();
            MessageBox.Show("成功");
        }
    }
}
