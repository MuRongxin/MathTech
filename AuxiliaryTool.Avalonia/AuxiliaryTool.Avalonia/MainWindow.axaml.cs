using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Media;
using AuxiliaryTool.Avalonia.Models;
using AuxiliaryTool.Avalonia.Views;
using System.IO;
using System.Linq;

namespace AuxiliaryTool.Avalonia
{
    public partial class MainWindow : Window
    {
        private OverviewView? _overviewView;
        private RandomView? _randomView;
        private ScoreAnalysisView? _scoreView;

        public MainWindow()
        {
            InitializeComponent();
        }

        protected override void OnLoaded(RoutedEventArgs e)
        {
            base.OnLoaded(e);
            LoadConfig();
        }

        private void LoadConfig()
        {
            var exeDir = Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);
            if (string.IsNullOrEmpty(exeDir)) return;

            var configPath = Path.Combine(exeDir, "Assets", "config.xml");
            if (!File.Exists(configPath))
            {
                configPath = Path.Combine(exeDir, "config.xml");
            }

            var paths = AuxiliaryMethods.Instance.ReadConfig(configPath);
            var basePath = Path.GetDirectoryName(configPath) ?? exeDir;

            AuxiliaryMethods.Instance.classFilePath_1 = Path.Combine(basePath, paths[0]);
            AuxiliaryMethods.Instance.classFilePath_2 = Path.Combine(basePath, paths[1]);

            var scorePath1 = Path.Combine(basePath, paths[2]);
            var scorePath2 = Path.Combine(basePath, paths[3]);

            // 预加载两个班级数据
            LoadClassData(1, AuxiliaryMethods.Instance.classFilePath_1, scorePath1);
            LoadClassData(2, AuxiliaryMethods.Instance.classFilePath_2, scorePath2);

            // 默认显示看板
            SwitchView("overview");
        }

        private void LoadClassData(int classIndex, string xmlPath, string excelPath)
        {
            if (classIndex == 1)
            {
                AuxiliaryMethods.Instance.studentDatas_1.Clear();
                AuxiliaryMethods.Instance.studentDatas_1_2.Clear();
                AuxiliaryMethods.Instance.ReadDataXml(xmlPath, AuxiliaryMethods.Instance.studentDatas_1);
                AuxiliaryMethods.Instance.ReadDataXml(xmlPath, AuxiliaryMethods.Instance.studentDatas_1_2);
                AuxiliaryMethods.Instance.ReadExcel(excelPath, AuxiliaryMethods.Instance.studentDatas_1);
                AuxiliaryMethods.Instance.ReadExcel(excelPath, AuxiliaryMethods.Instance.studentDatas_1_2, 1);
            }
            else
            {
                AuxiliaryMethods.Instance.studentDatas_2.Clear();
                AuxiliaryMethods.Instance.studentDatas_2_2.Clear();
                AuxiliaryMethods.Instance.ReadDataXml(xmlPath, AuxiliaryMethods.Instance.studentDatas_2);
                AuxiliaryMethods.Instance.ReadDataXml(xmlPath, AuxiliaryMethods.Instance.studentDatas_2_2);
                AuxiliaryMethods.Instance.ReadExcel(excelPath, AuxiliaryMethods.Instance.studentDatas_2);
                AuxiliaryMethods.Instance.ReadExcel(excelPath, AuxiliaryMethods.Instance.studentDatas_2_2, 1);
            }
        }

        private void ClassButton_Click(object? sender, RoutedEventArgs e)
        {
            if (sender is Button btn)
            {
                if (btn.Name == "ClassAButton")
                {
                    AuxiliaryMethods.Instance.currentClass = 1;
                    AuxiliaryMethods.Instance.studentDatas = AuxiliaryMethods.Instance.studentDatas_1;
                    HighlightClassButton(ClassAButton, ClassBButton);
                }
                else
                {
                    AuxiliaryMethods.Instance.currentClass = 2;
                    AuxiliaryMethods.Instance.studentDatas = AuxiliaryMethods.Instance.studentDatas_2;
                    HighlightClassButton(ClassBButton, ClassAButton);
                }
            }
        }

        private void HighlightClassButton(Button active, Button inactive)
        {
            active.Opacity = 1.0;
            inactive.Opacity = 0.5;
        }

        private void NavButton_Click(object? sender, RoutedEventArgs e)
        {
            if (sender is Button btn)
            {
                ResetNavButtons();
                btn.Foreground = Brushes.White;
                switch (btn.Name)
                {
                    case "NavOverview": SwitchView("overview"); break;
                    case "NavRandom": SwitchView("random"); break;
                    case "NavScore": SwitchView("score"); break;
                }
            }
        }

        private void ResetNavButtons()
        {
            NavOverview.Foreground = new SolidColorBrush(Color.Parse("#FFAAAAAA"));
            NavRandom.Foreground = new SolidColorBrush(Color.Parse("#FFAAAAAA"));
            NavScore.Foreground = new SolidColorBrush(Color.Parse("#FFAAAAAA"));
        }

        private void SwitchView(string viewName)
        {
            switch (viewName)
            {
                case "overview":
                    _overviewView ??= new OverviewView();
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

        private void TitleBar_PointerPressed(object? sender, PointerPressedEventArgs e)
        {
            if (e.GetCurrentPoint(this).Properties.IsLeftButtonPressed)
            {
                BeginMoveDrag(e);
            }
        }

        private void CloseButton_Click(object? sender, RoutedEventArgs e)
        {
            Close();
        }
    }
}
