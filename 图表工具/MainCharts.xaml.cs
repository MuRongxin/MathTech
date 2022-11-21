using LiveCharts;
using LiveCharts.Defaults;
using LiveCharts.Wpf;
using System;
using System.Collections.Generic;
using System.Drawing.Drawing2D;
using System.Linq;
using System.Text;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using 图表工具.Helper;
using 图表工具.LocalData;

namespace 图表工具
{
    /// <summary>
    /// MainWindow.xaml 的交互逻辑
    /// </summary>
    public partial class MainCharts : Window
    {
        public MainCharts()
        {
            InitializeComponent();
        }

        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            //UpdateDataContext();
            Global.MainCharts = this;
            LoadDataManagerForm();
        }

        class ChartInfo
        {
            public ChartValues<ObservableValue> Values { get; set; }
            public List<double> BaseValues { get; set; }
            public double Scale { get; set; }
        }

        public void UpdateDataContext(DateTime _startDay, DateTime _endDay)
        {
            SeriesCollection series = new SeriesCollection();

            var resultData = ReportData.ResportDatas.FindAll(c => c.ReportDate >= _startDay && c.ReportDate <= _endDay);

            Dictionary<string, ChartInfo> linesDic = new Dictionary<string, ChartInfo>();
            string[] labs = new string[resultData.Count];

            double _maxAbsValue = 0;

            try
            {
                _maxAbsValue = Convert.ToDouble(txtMaxAbsValue.Text);
            }
            catch
            {
                MessageBox.Show("请正确输入最大相对值");
                txtMaxAbsValue.Focus();
                txtMaxAbsValue.SelectAll();
                return;
            }

            for (int i = 0; i < Global.ColumnNameList.Count; i++)
            {
                string _columnName = Global.ColumnNameList[i];

                linesDic.Add(_columnName, new ChartInfo()
                {
                    Values = new ChartValues<ObservableValue>(),
                    BaseValues = new List<double>(),
                    Scale = 1
                });

                for (int j = 0; j < resultData.Count; j++)
                {
                    var _model = resultData[j];

                    double _baseValue = _model.Columns.Find(c => c.ColumnName == _columnName).ColumnValue;

                    linesDic[_columnName].BaseValues.Add(_baseValue);
                }
            }

            int _ranIndex = 0;
            foreach (var key in linesDic.Keys)
            {
                double _max = linesDic[key].BaseValues.Max(c => Math.Abs(c));
                if (_max > _maxAbsValue || _max < _maxAbsValue * -1)
                {
                    linesDic[key].Scale = (_maxAbsValue - _ranIndex * 10) / _max;
                }

                for (int i = 0; i < linesDic[key].BaseValues.Count; i++)
                {
                    linesDic[key].Values.Add(new ObservableValue(Math.Round(linesDic[key].BaseValues[i] * linesDic[key].Scale, 2)));
                }

                _ranIndex += 1;
            }

            for (int i = 0; i < resultData.Count; i++)
            {
                var _model = resultData[i];
                labs[i] = _model.ReportDate.ToString("yyMMdd");
            }

            foreach (var key in linesDic.Keys)
            {
                if (key == "成交量")
                {
                    //var _line = new StepLineSeries();
                    var _line = new ColumnSeries();
                    _line.Title = key;
                    _line.Values = linesDic[key].Values;
                    _line.DataLabels = true;
                    _line.LabelPoint = point => $"{linesDic[key].BaseValues[(int)point.X]}";
                    if (!(bool)cbUseColor.IsChecked)
                    {
                        _line.Fill = Brushes.Transparent;
                    }
                    series.Add(_line);
                }
                else 
                {
                    //var _line = new StepLineSeries();
                    var _line = new LineSeries();
                    _line.Title = key;
                    _line.Values = linesDic[key].Values;
                    _line.DataLabels = true;
                    _line.LabelPoint = point => $"{linesDic[key].BaseValues[(int)point.X]}";
                    if (!(bool)cbUseColor.IsChecked)
                    {
                        _line.Fill = Brushes.Transparent;
                    }
                    series.Add(_line);
                }
            }

            SeriesCollection = series;

            Labels = labs;

            //Formatter = value => $"相对 {value}";

            PointLabel = chartPoint =>
    string.Format("{0} ({1:P})", chartPoint.Y, chartPoint.Participation);

            DataContext = null;
            DataContext = this;
        }

        public SeriesCollection SeriesCollection { get; set; }
        public string[] Labels { get; set; }
        public Func<double, string> Formatter { get; set; }
        public Func<ChartPoint, string> PointLabel { get; set; }

        private void UpdateAllOnClick(object sender, RoutedEventArgs e)
        {
            var r = new Random();

            foreach (var series in SeriesCollection)
            {
                foreach (var observable in series.Values.Cast<ObservableValue>())
                {
                    observable.Value = r.Next(0, 10);
                }
            }
        }

        private void Chart_OnDataClick(object sender, ChartPoint point)
        {
            //point instance contains many useful information...
            //sender is the shape that called the event.

            MessageBox.Show("You clicked " + point.X + ", " + point.Y);

        }

        private void btnDataManager_Click(object sender, RoutedEventArgs e)
        {
            LoadDataManagerForm();
        }

        private void LoadDataManagerForm()
        {
            DataManager manager = new DataManager();
            manager.ShowDialog();
        }

        private void btnReLoad_Click(object sender, RoutedEventArgs e)
        {
            if (Global.ColumnNameList.Count == 0)
            {
                MessageBox.Show("当前未选中任何图表项");
                return;
            }
            DateTime _startDay = (DateTime)dpStartDay.SelectedDate;
            DateTime _endDay = (DateTime)dpEndDay.SelectedDate;
            UpdateDataContext(_startDay, _endDay);
        }

        public void UpdateDataContext()
        {
            if (ReportData.ResportDatas.Count > 0) 
            {
                dpStartDay.SelectedDate = ReportData.ResportDatas.Min(c => c.ReportDate);
                dpEndDay.SelectedDate = ReportData.ResportDatas.Max(c => c.ReportDate);
            }
        }

        private void btnSearch_Click(object sender, RoutedEventArgs e)
        {
            SearchCondition search = new SearchCondition();
            search.ShowDialog();
        }
    }
}
