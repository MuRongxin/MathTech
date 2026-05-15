using Avalonia;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Media;
using Avalonia.Threading;
using AuxiliaryTool.Avalonia.Models;
using System;
using System.Collections.Generic;
using System.Linq;

namespace AuxiliaryTool.Avalonia.Views
{
    public partial class RandomView : UserControl
    {
        private DispatcherTimer? _timer;
        private Random _random = new Random();
        private StudentData? _currentStudent;
        private List<StudentData> _resultList = new List<StudentData>();
        private bool _isRunning = false;

        public RandomView()
        {
            InitializeComponent();
            _timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(50) };
            _timer.Tick += Timer_Tick;
        }

        private void Timer_Tick(object? sender, EventArgs e)
        {
            var datas = AuxiliaryMethods.Instance.studentDatas;
            if (datas.Count == 0) return;
            int idx = _random.Next(datas.Count);
            ResultLabel.Text = datas[idx].Name;
            ResultLabel.Foreground = new SolidColorBrush(ThemeColor.RandomColor());
        }

        private void StartButton_Click(object? sender, RoutedEventArgs e)
        {
            if (!_isRunning)
            {
                var datas = AuxiliaryMethods.Instance.studentDatas;
                if (datas.Count == 0) return;

                _isRunning = true;
                StartButton.Content = "停止";
                _timer?.Start();
            }
            else
            {
                _isRunning = false;
                StartButton.Content = "开始随机";
                _timer?.Stop();

                GetRandomResult();
                if (_currentStudent != null)
                {
                    ResultLabel.Text = _currentStudent.Name;
                    ResultLabel.Foreground = Brushes.White;

                    // 更新 callCount
                    if (AuxiliaryMethods.Instance.currentClass == 1)
                        AuxiliaryMethods.Instance.UpdateXmlData(
                            AuxiliaryMethods.Instance.classFilePath_1,
                            _currentStudent.ID,
                            _currentStudent.CallCount + 1);
                    else
                        AuxiliaryMethods.Instance.UpdateXmlData(
                            AuxiliaryMethods.Instance.classFilePath_2,
                            _currentStudent.ID,
                            _currentStudent.CallCount + 1);

                    _currentStudent.CallCount++;
                    AddHistory(_currentStudent.Name, _currentStudent.CallCount);
                }
            }
        }

        private void GetRandomResult()
        {
            var datas = AuxiliaryMethods.Instance.studentDatas;
            if (datas.Count == 0) return;

            while (true)
            {
                int idx = _random.Next(datas.Count);
                var stu = datas[idx];
                if (!_resultList.Contains(stu))
                {
                    _currentStudent = stu;
                    _resultList.Add(stu);
                    break;
                }
                if (_resultList.Count >= datas.Count)
                {
                    _resultList.Clear();
                }
            }
        }

        private void AddHistory(string name, int callCount)
        {
            var block = new TextBlock
            {
                Text = $" {name}  [{callCount}]",
                FontSize = 16,
                Foreground = new SolidColorBrush(ThemeColor.RandomColor()),
                Margin = new Thickness(0, 2)
            };
            HistoryPanel.Children.Insert(0, block);
        }
    }
}
