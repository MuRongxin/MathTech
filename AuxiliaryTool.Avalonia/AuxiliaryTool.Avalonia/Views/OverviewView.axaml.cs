using Avalonia.Controls;
using Avalonia.Interactivity;
using AuxiliaryTool.Avalonia.Models;
using System.Linq;

namespace AuxiliaryTool.Avalonia.Views
{
    public partial class OverviewView : UserControl
    {
        public OverviewView()
        {
            InitializeComponent();
            Loaded += OnLoaded;
        }

        private void OnLoaded(object? sender, RoutedEventArgs e)
        {
            RefreshData();
        }

        public void RefreshData()
        {
            A01Count.Text = AuxiliaryMethods.Instance.studentDatas_1.Count.ToString();
            A02Count.Text = AuxiliaryMethods.Instance.studentDatas_2.Count.ToString();

            double avg1 = 0, avg2 = 0;
            if (AuxiliaryMethods.Instance.studentDatas_1.Count > 0 && AuxiliaryMethods.Instance.studentDatas_1[0].scoreArr.Count > 0)
            {
                var scores = AuxiliaryMethods.Instance.studentDatas_1.SelectMany(s => s.scoreArr.Select(a => double.Parse(a[1])));
                avg1 = scores.Average();
            }
            if (AuxiliaryMethods.Instance.studentDatas_2.Count > 0 && AuxiliaryMethods.Instance.studentDatas_2[0].scoreArr.Count > 0)
            {
                var scores = AuxiliaryMethods.Instance.studentDatas_2.SelectMany(s => s.scoreArr.Select(a => double.Parse(a[1])));
                avg2 = scores.Average();
            }

            A01Avg.Text = $"平均分: {avg1:F2}";
            A02Avg.Text = $"平均分: {avg2:F2}";

            if (AuxiliaryMethods.Instance.studentDatas_1.Count > 0 && AuxiliaryMethods.Instance.studentDatas_1[0].scoreArr.Count > 0)
            {
                var dates = AuxiliaryMethods.Instance.studentDatas_1[0].scoreArr.Select(a => a[0]).ToList();
                RecentDates.Text = string.Join("  |  ", dates);
            }
        }
    }
}
