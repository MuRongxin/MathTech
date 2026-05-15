using Avalonia;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Media;
using AuxiliaryTool.Avalonia.Models;
using AuxiliaryTool.Avalonia.Views;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;

namespace AuxiliaryTool.Avalonia
{
    public class ClassStudentDto
    {
        public int id { get; set; }
        public string name { get; set; } = "";
        public int callCount { get; set; }
        public int scoreCount { get; set; }
    }

    public class ScoresApiDto
    {
        public List<string> dates { get; set; } = new();
        public List<StudentScoreDto> students { get; set; } = new();
    }

    public class StudentScoreDto
    {
        public string name { get; set; } = "";
        public List<double> scores { get; set; } = new();
    }

    public class RandomResultDto
    {
        public int id { get; set; }
        public string name { get; set; } = "";
        public int callCount { get; set; }
    }

    public partial class MainWindow : Window
    {
        private OverviewView? _overviewView;
        private RandomView? _randomView;
        private ScoreAnalysisView? _scoreView;
        private Button? _activeNavButton;

        public static readonly HttpClient HttpClient = new HttpClient
        {
            BaseAddress = new Uri("http://localhost:5002/"),
            Timeout = TimeSpan.FromSeconds(30)
        };

        public MainWindow()
        {
            InitializeComponent();
        }

        protected override async void OnLoaded(RoutedEventArgs e)
        {
            base.OnLoaded(e);
            await LoadDataFromApiAsync();
        }

        private async Task LoadDataFromApiAsync()
        {
            try
            {
                // Load class basic info
                var class1 = await HttpClient.GetFromJsonAsync<List<ClassStudentDto>>("api/class/1");
                var class2 = await HttpClient.GetFromJsonAsync<List<ClassStudentDto>>("api/class/2");

                // Load scores (objective)
                var scores1 = await HttpClient.GetFromJsonAsync<ScoresApiDto>("api/scores/1");
                var scores2 = await HttpClient.GetFromJsonAsync<ScoresApiDto>("api/scores/2");

                // Load scores (full)
                var scores1Full = await HttpClient.GetFromJsonAsync<ScoresApiDto>("api/scores/1?fullScore=true");
                var scores2Full = await HttpClient.GetFromJsonAsync<ScoresApiDto>("api/scores/2?fullScore=true");

                FillStudentData(class1, scores1, AuxiliaryMethods.Instance.studentDatas_1);
                FillStudentData(class2, scores2, AuxiliaryMethods.Instance.studentDatas_2);
                FillStudentData(class1, scores1Full, AuxiliaryMethods.Instance.studentDatas_1_2);
                FillStudentData(class2, scores2Full, AuxiliaryMethods.Instance.studentDatas_2_2);

                AuxiliaryMethods.Instance.currentClass = 1;
                AuxiliaryMethods.Instance.studentDatas = AuxiliaryMethods.Instance.studentDatas_1;

                SwitchView("overview");
            }
            catch (Exception ex)
            {
                var dialog = new Window
                {
                    Title = "Error",
                    Width = 400,
                    Height = 200,
                    Content = new TextBlock
                    {
                        Text = "无法连接到后端服务:\n" + ex.Message + "\n\n请确保后端服务已启动:\ncd AuxiliaryTool.Web && dotnet run --urls http://localhost:5002",
                        Margin = new Thickness(20),
                        TextWrapping = TextWrapping.Wrap
                    }
                };
                dialog.ShowDialog(this);
            }
        }

        private void FillStudentData(List<ClassStudentDto>? classData, ScoresApiDto? scoresData, List<StudentData> target)
        {
            target.Clear();
            if (classData == null) return;

            foreach (var c in classData)
            {
                target.Add(new StudentData(c.id, c.name, c.callCount));
            }

            if (scoresData?.students != null && scoresData.dates != null)
            {
                foreach (var s in scoresData.students)
                {
                    var stu = target.FirstOrDefault(x => x.Name == s.name);
                    if (stu != null)
                    {
                        int count = Math.Min(scoresData.dates.Count, s.scores.Count);
                        for (int i = 0; i < count; i++)
                        {
                            stu.scoreArr.Add(new string[] { scoresData.dates[i], s.scores[i].ToString("F2") });
                            stu.scoreList.Add(new Dictionary<string, string> { { scoresData.dates[i], s.scores[i].ToString("F2") } });
                        }
                    }
                }
            }
        }

        private void NavButton_Click(object? sender, RoutedEventArgs e)
        {
            if (sender is Button btn)
            {
                _activeNavButton?.Classes.Remove("active");
                btn.Classes.Add("active");
                _activeNavButton = btn;

                switch (btn.Name)
                {
                    case "NavOverview": SwitchView("overview"); break;
                    case "NavRandom": SwitchView("random"); break;
                    case "NavScore": SwitchView("score"); break;
                }
            }
        }

        private void SwitchView(string viewName)
        {
            switch (viewName)
            {
                case "overview":
                    _overviewView ??= new OverviewView();
                    _overviewView.RefreshData();
                    MainContent.Content = _overviewView;
                    break;
                case "random":
                    _randomView ??= new RandomView();
                    MainContent.Content = _randomView;
                    break;
                case "score":
                    _scoreView ??= new ScoreAnalysisView();
                    MainContent.Content = _scoreView;
                    break;
            }
        }
    }
}
