using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Media;
using LiveChartsCore;
using LiveChartsCore.SkiaSharpView;
using LiveChartsCore.SkiaSharpView.Painting;
using AuxiliaryTool.Avalonia.Models;
using SkiaSharp;
using System;
using System.Collections.Generic;
using System.Linq;

namespace AuxiliaryTool.Avalonia.Views
{
    public partial class ScoreAnalysisView : UserControl
    {
        private List<StudentData> _currentList = new List<StudentData>();
        private int _displayIndex = 0;
        private int _displayLength = 0;
        private bool _isLastWeek = false;
        private List<ISeries> _originalSeries = new List<ISeries>();
        private List<string> _dates = new List<string>();

        public ScoreAnalysisView()
        {
            InitializeComponent();
            Loaded += OnLoaded;
            StudentBox.SelectionChanged += StudentBox_SelectionChanged;
        }

        private void OnLoaded(object? sender, RoutedEventArgs e)
        {
            _currentList = AuxiliaryMethods.Instance.studentDatas;
            InitChartFormat();
            InitStudentBox();
            FirstChart();
        }

        private void InitChartFormat()
        {
            if (_currentList.Count == 0 || _currentList[0].scoreArr.Count == 0) return;

            _dates = _currentList[0].scoreArr.Select(a => a[0].Split(' ')[0]).ToList();

            Chart.XAxes = new[]
            {
                new Axis
                {
                    Labels = _dates.ToArray(),
                    Name = "Examination",
                    LabelsPaint = new SolidColorPaint(SKColors.LightGray),
                    NamePaint = new SolidColorPaint(SKColors.LightGray),
                    TextSize = 12
                }
            };

            Chart.YAxes = new[]
            {
                new Axis
                {
                    Name = "Percentage of Score",
                    LabelsPaint = new SolidColorPaint(SKColors.LightGray),
                    NamePaint = new SolidColorPaint(SKColors.LightGray),
                    TextSize = 12
                }
            };

            Chart.LegendTextPaint = new SolidColorPaint(SKColors.LightGray);
            Chart.Background = new SolidColorBrush(Color.Parse("#FF252525"));
        }

        private void InitStudentBox()
        {
            StudentBox.Items.Clear();
            foreach (var stu in _currentList)
            {
                StudentBox.Items.Add(stu.Name);
            }
        }

        private void FirstChart()
        {
            if (_currentList == null || _currentList.Count == 0) return;

            Chart.Series = Array.Empty<ISeries>();
            _displayIndex = 0;

            var random = new Random();
            int count = Math.Min(random.Next(3, 7), _currentList.Count);
            var used = new HashSet<int>();

            var seriesList = new List<ISeries>();
            for (int i = 0; i < count; i++)
            {
                int idx = random.Next(_currentList.Count);
                if (used.Contains(idx)) continue;
                used.Add(idx);
                seriesList.Add(CreateSeries(_currentList[idx]));
            }

            Chart.Series = seriesList.ToArray();
            _displayIndex = used.Count > 0 ? used.Max() + 1 : 0;
        }

        private ISeries CreateSeries(StudentData student)
        {
            var values = student.scoreArr.Select(a => double.Parse(a[1])).ToList();
            if (_isLastWeek && values.Count >= 7)
            {
                values = values.Skip(values.Count - 7).ToList();
            }

            return new LineSeries<double>
            {
                Values = values,
                Name = student.Name,
                GeometrySize = 8,
                LineSmoothness = 0,
                Stroke = new SolidColorPaint(SKColor.FromHsv((float)_random.Next(360), 80, 90), 2),
                Fill = null
            };
        }

        private void NextGroup_Click(object? sender, RoutedEventArgs e)
        {
            if (_displayLength == 0) _displayLength = _currentList.Count;

            var seriesList = Chart.Series?.ToList() ?? new List<ISeries>();
            for (int i = _displayIndex; i < _displayIndex + _displayLength; i++)
            {
                if (i >= _currentList.Count) break;
                seriesList.Add(CreateSeries(_currentList[i]));
            }
            _displayIndex += _displayLength;
            if (_displayIndex >= _currentList.Count) _displayIndex = 0;

            Chart.Series = seriesList.ToArray();
        }

        private void Clear_Click(object? sender, RoutedEventArgs e)
        {
            Chart.Series = Array.Empty<ISeries>();
            StudentBox.SelectedIndex = -1;
        }

        private void LastWeek_Click(object? sender, RoutedEventArgs e)
        {
            if (!_isLastWeek)
            {
                _isLastWeek = true;
                _originalSeries = Chart.Series?.ToList() ?? new List<ISeries>();

                var lastWeekDates = _dates.Skip(_dates.Count - 7).ToList();
                Chart.XAxes = new[]
                {
                    new Axis
                    {
                        Labels = lastWeekDates.ToArray(),
                        Name = "Examination",
                        LabelsPaint = new SolidColorPaint(SKColors.LightGray),
                        NamePaint = new SolidColorPaint(SKColors.LightGray)
                    }
                };

                var filtered = new List<ISeries>();
                foreach (var s in Chart.Series ?? Array.Empty<ISeries>())
                {
                    if (s is LineSeries<double> ls && ls.Values is IEnumerable<double> vals)
                    {
                        var list = vals.ToList();
                        if (list.Count >= 7)
                        {
                            ls.Values = list.Skip(list.Count - 7).ToList();
                            filtered.Add(ls);
                        }
                    }
                }
                Chart.Series = filtered.ToArray();
                LastWeekButton.Content = "全部";
            }
            else
            {
                _isLastWeek = false;
                Chart.XAxes = new[]
                {
                    new Axis
                    {
                        Labels = _dates.ToArray(),
                        Name = "Examination",
                        LabelsPaint = new SolidColorPaint(SKColors.LightGray),
                        NamePaint = new SolidColorPaint(SKColors.LightGray)
                    }
                };
                Chart.Series = _originalSeries.ToArray();
                LastWeekButton.Content = "最近7次";
            }
        }

        private void HalfScore_Click(object? sender, RoutedEventArgs e)
        {
            if (AuxiliaryMethods.Instance.currentClass == 1)
                _currentList = AuxiliaryMethods.Instance.studentDatas_1;
            else
                _currentList = AuxiliaryMethods.Instance.studentDatas_2;
            Refresh();
        }

        private void AllScore_Click(object? sender, RoutedEventArgs e)
        {
            if (AuxiliaryMethods.Instance.currentClass == 1)
                _currentList = AuxiliaryMethods.Instance.studentDatas_1_2;
            else
                _currentList = AuxiliaryMethods.Instance.studentDatas_2_2;
            Refresh();
        }

        private void Refresh()
        {
            _displayIndex = 0;
            InitChartFormat();
            InitStudentBox();
            FirstChart();
        }

        private void StudentBox_SelectionChanged(object? sender, SelectionChangedEventArgs e)
        {
            if (StudentBox.SelectedItem == null) return;
            var name = StudentBox.SelectedItem.ToString();
            var student = _currentList.FirstOrDefault(s => s.Name == name);
            if (student == null) return;

            var seriesList = Chart.Series?.ToList() ?? new List<ISeries>();
            seriesList.Add(CreateSeries(student));
            Chart.Series = seriesList.ToArray();
        }

        private void DisplayCountBox_SelectionChanged(object? sender, SelectionChangedEventArgs e)
        {
            if (_currentList == null || _currentList.Count == 0) return;
            var item = DisplayCountBox.SelectedItem as ComboBoxItem;
            if (item == null) return;
            var text = item.Content?.ToString();
            if (text == "All")
                _displayLength = _currentList.Count;
            else
                int.TryParse(text, out _displayLength);
            _displayIndex = 0;
        }

        private static Random _random = new Random();
    }
}
