using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using LiveCharts;
using LiveCharts.Defaults;
using LiveCharts.Wpf;


namespace Auxiliary_tool
{
    public partial class Score_Analysis_Panle : UserControl
    {
        public Score_Analysis_Panle()
        {
            InitializeComponent();
        }

        private void Score_Analysis_Load(object sender, EventArgs e)
        {
            
            cartesianChart.AxisX.Add(new Axis
            {
                Title = "Examination",
                Labels = new[] { "2022/12/09", "2022/12/10", "2022/12/11", "2022/12/12", "2022/12/13" }
            });

            cartesianChart.AxisY.Add(new Axis
            {
                Title = "Percentage of Score",
               //LabelFormatter = value => value.ToString("C"),
            });
            cartesianChart.LegendLocation=LegendLocation.Right;
        }

        private void charttestButton_Click(object sender, EventArgs e)
        {
            DrawChart(Auxiliarymethods.Instance.studentDatas);

        }

        Dictionary<string, List<double>> scoreDic = new Dictionary<string, List<double>>();

        private void DrawChart(List<StudentData> studentDatas)
        {
            cartesianChart.Series.Clear();
            SeriesCollection seriesCollection = new SeriesCollection();

            foreach (var item in studentDatas)
            {
                List<double> scoreList = new List<double>();
                string name = item.Name;
                //foreach (var dicVal in item.scoreDic)
                //{
                //    foreach (var score in dicVal)
                //    {
                //        scoreList.Add(float.Parse(score.Value.ToString()));
                //    }
                //}
                foreach (var dicVal in item.scoreArr)
                {
                    double res = double.Parse(dicVal[1]);
                    scoreList.Add(res);                   
                }

                scoreDic.Add(name, scoreList);
                seriesCollection.Add(new LineSeries() { Title = name, Values = new ChartValues<double>(scoreList), DataLabels = false });
            }
            //List<double> scoreList_1 = new List<double>() { 0.11, 0.21, 0.41, 0.21, 0.43, 0.56, 1.76, 0.01, 0.12, 0.45, 1};
            //seriesCollection.Add(new LineSeries() { Title = "绫小路", Values = new ChartValues<double>(scoreList_1), DataLabels = false });
            
            cartesianChart.Series = seriesCollection;
        }

        private void ReDrawChart(int displayLenth)
        {
            cartesianChart.Series.Clear();
            SeriesCollection seriesCollection = new SeriesCollection();

            cartesianChart.Series = seriesCollection;

            for (int i = 0; i < displayLenth; i++)
            {

            }
        }

        private void displayDataLenthComboBox_SelectedIndexChanged(object sender, EventArgs e)
        {
             displayDataLenthComboBox.SelectedItem.ToString();
        }

        private void scoreFluctuationComboBox_SelectedIndexChanged(object sender, EventArgs e)
        {

        }
    }
}
