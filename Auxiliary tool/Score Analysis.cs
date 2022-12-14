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

        Dictionary<string, List<float>> scoreDic = new Dictionary<string, List<float>>();

        private void DrawChart(List<StudentData> studentDatas)
        {
            cartesianChart.Series.Clear();
            SeriesCollection seriesCollection = new SeriesCollection();

            foreach (var item in studentDatas)
            {
                List<float> scoreList = new List<float>();
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
                    float res = float.Parse(dicVal[1]);
                    scoreList.Add(res);                   
                }               

                // scoreDic.Add(name, scoreList);
                //seriesCollection.Add(new LineSeries() { Title = name, Values = new ChartValues<float>(scoreList), DataLabels = false });
            }
            List<float> scoreList_1 = new List<float>() { 0.11f, 0.21f, 0.41f, 0.21f, 0.43f, 1.56f, 1.76f, 0.01f, 0.12f, 0.45f, 1f,};
            seriesCollection.Add(new LineSeries() { Title = "绫小路", Values = new ChartValues<float>(scoreList_1), DataLabels = false });
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
