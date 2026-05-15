using Avalonia;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Media;
using Avalonia.Threading;
using AuxiliaryTool.Avalonia.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http.Json;
using System.Threading.Tasks;

namespace AuxiliaryTool.Avalonia.Views
{
    public partial class RandomView : UserControl
    {
        private DispatcherTimer? _timer;
        private Random _random = new Random();
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

        private async void StartButton_Click(object? sender, RoutedEventArgs e)
        {
            if (!_isRunning)
            {
                var datas = AuxiliaryMethods.Instance.studentDatas;
                if (datas.Count == 0) return;

                _isRunning = true;
                StartRandomButton.Content = "Stop";
                StartRandomButton.Background = new SolidColorBrush(Color.Parse("#FFE74C3C"));
                StartRandomButton.Foreground = Brushes.White;
                _timer?.Start();
            }
            else
            {
                _isRunning = false;
                StartRandomButton.Content = "Start Random";
                StartRandomButton.Background = new SolidColorBrush(Color.Parse("#FFE8E8E8"));
                StartRandomButton.Foreground = new SolidColorBrush(Color.Parse("#FF888888"));
                _timer?.Stop();

                await DoRandomAsync();
            }
        }

        private async Task DoRandomAsync()
        {
            try
            {
                var result = await MainWindow.HttpClient.PostAsJsonAsync<object>(
                    $"api/random/{AuxiliaryMethods.Instance.currentClass}", new { });
                var data = await result.Content.ReadFromJsonAsync<RandomResultApiDto>();
                if (data == null) return;

                ResultLabel.Text = data.name;
                ResultLabel.Foreground = new SolidColorBrush(Color.Parse("#FF333333"));

                // Update local callCount
                var stu = AuxiliaryMethods.Instance.studentDatas.FirstOrDefault(s => s.ID == data.id);
                if (stu != null) stu.CallCount = data.callCount;
                stu = AuxiliaryMethods.Instance.currentClass == 1
                    ? AuxiliaryMethods.Instance.studentDatas_1.FirstOrDefault(s => s.ID == data.id)
                    : AuxiliaryMethods.Instance.studentDatas_2.FirstOrDefault(s => s.ID == data.id);
                if (stu != null) stu.CallCount = data.callCount;

                AddHistory(data.name, data.callCount);
            }
            catch (Exception ex)
            {
                ResultLabel.Text = "抽人失败:\n" + ex.Message;
                ResultLabel.Foreground = Brushes.Red;
            }
        }

        private void AddHistory(string name, int callCount)
        {
            var block = new TextBlock
            {
                Text = $" {name}  [{callCount}]",
                FontSize = 15,
                Foreground = new SolidColorBrush(ThemeColor.RandomColor()),
                Margin = new Thickness(0, 4)
            };
            HistoryPanel.Children.Insert(0, block);
        }
    }

    public class RandomResultApiDto
    {
        public int id { get; set; }
        public string name { get; set; } = "";
        public int callCount { get; set; }
    }
}
