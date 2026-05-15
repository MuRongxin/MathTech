using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Media;
using AuxiliaryTool.Avalonia.Models;
using LiveChartsCore.SkiaSharpView;
using LiveChartsCore.SkiaSharpView.Painting;
using SkiaSharp;
using System;
using System.Linq;
using System.Net.Http.Json;

namespace AuxiliaryTool.Avalonia.Views
{
    public partial class OverviewView : UserControl
    {
        public OverviewView()
        {
            InitializeComponent();
            Loaded += OnLoaded;
        }

        private async void OnLoaded(object? sender, RoutedEventArgs e)
        {
            RefreshData();
            await LoadChartDataAsync();
        }

        public void RefreshData()
        {
            var a1 = AuxiliaryMethods.Instance.studentDatas_1;
            var a2 = AuxiliaryMethods.Instance.studentDatas_2;

            DataLengthLabel1.Text = a1.Count.ToString();
            DataLengthLabel2.Text = a2.Count.ToString();

            double avg1 = 0, avg2 = 0;
            if (a1.Count > 0 && a1[0].scoreArr.Count > 0)
            {
                var scores = a1.SelectMany(s => s.scoreArr.Select(a => double.Parse(a[1])));
                avg1 = scores.Average();
            }
            if (a2.Count > 0 && a2[0].scoreArr.Count > 0)
            {
                var scores = a2.SelectMany(s => s.scoreArr.Select(a => double.Parse(a[1])));
                avg2 = scores.Average();
            }

            SubLabel1.Text = $"平均分: {avg1:F2}";
            SubLabel2.Text = $"平均分: {avg2:F2}";

            var dates = a1.Count > 0 && a1[0].scoreArr.Count > 0
                ? a1[0].scoreArr.Select(a => a[0]).ToList()
                : new System.Collections.Generic.List<string>();

            DateLabel.Text = dates.Count > 0 ? dates.Last() : "--";
        }

        private async System.Threading.Tasks.Task LoadChartDataAsync()
        {
            try
            {
                var data = await MainWindow.HttpClient.GetFromJsonAsync<OverviewApiDto>("api/overview");
                if (data == null || data.dates == null || data.dates.Count == 0) return;

                AverageChart.XAxes = new[]
                {
                    new Axis
                    {
                        Labels = data.dates.ToArray(),
                        LabelsPaint = new SolidColorPaint(SKColors.Gray),
                        TextSize = 10
                    }
                };
                AverageChart.YAxes = new[]
                {
                    new Axis
                    {
                        MinLimit = 0,
                        MaxLimit = 1,
                        LabelsPaint = new SolidColorPaint(SKColors.Gray),
                        TextSize = 10
                    }
                };

                AverageChart.Series = new LiveChartsCore.ISeries[]
                {
                    new LineSeries<double>
                    {
                        Values = data.averages1 ?? new System.Collections.Generic.List<double>(),
                        Name = "A01 平均分",
                        Stroke = new SolidColorPaint(SKColor.Parse("#1EAEE7"), 2),
                        Fill = new SolidColorPaint(SKColor.Parse("#1EAEE7").WithAlpha(30)),
                        GeometrySize = 4,
                        LineSmoothness = 0.3
                    },
                    new LineSeries<double>
                    {
                        Values = data.averages2 ?? new System.Collections.Generic.List<double>(),
                        Name = "A02 平均分",
                        Stroke = new SolidColorPaint(SKColor.Parse("#39C5BB"), 2),
                        Fill = new SolidColorPaint(SKColor.Parse("#39C5BB").WithAlpha(30)),
                        GeometrySize = 4,
                        LineSmoothness = 0.3
                    }
                };

                AverageChart.LegendTextPaint = new SolidColorPaint(SKColors.DimGray);
            }
            catch { /* ignore chart errors */ }
        }

        private void ClassButton_Click(object? sender, RoutedEventArgs e)
        {
            if (sender is Button btn)
            {
                if (btn.Name == "SelectA01Btn")
                {
                    AuxiliaryMethods.Instance.currentClass = 1;
                    AuxiliaryMethods.Instance.studentDatas = AuxiliaryMethods.Instance.studentDatas_1;
                    SelectA01Btn.Opacity = 1.0;
                    SelectA02Btn.Opacity = 0.6;
                }
                else
                {
                    AuxiliaryMethods.Instance.currentClass = 2;
                    AuxiliaryMethods.Instance.studentDatas = AuxiliaryMethods.Instance.studentDatas_2;
                    SelectA01Btn.Opacity = 0.6;
                    SelectA02Btn.Opacity = 1.0;
                }
            }
        }
    }

    public class OverviewApiDto
    {
        public object a01 { get; set; } = new();
        public object a02 { get; set; } = new();
        public System.Collections.Generic.List<string> dates { get; set; } = new();
        public System.Collections.Generic.List<double> averages1 { get; set; } = new();
        public System.Collections.Generic.List<double> averages2 { get; set; } = new();
    }
}
