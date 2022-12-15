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
            displayDataLenthComboBox.SelectedIndex = 0;//默认显示的数据量；
                     
            SetChartFormat();

            //DrawChart(Auxiliarymethods.Instance.studentDatas_1);
        }

        private void charttestButton_Click(object sender, EventArgs e)
        {
            DrawChart(Auxiliarymethods.Instance.studentDatas_1);

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
                //        scoreList.Add(double.Parse(score.Value.ToString()));
                //    }
                //}

                // 使用另一种记录日期和成绩的方式；
                foreach (var dicVal in item.scoreArr)
                    scoreList.Add(double.Parse(dicVal[1]));


                scoreDic.Add(name, scoreList);
                seriesCollection.Add(new LineSeries() { Title = name, Values = new ChartValues<double>(scoreList), DataLabels = false });
            }
            //List<double> scoreList_1 = new List<double>() { 0.11, 0.21, 0.41, 0.21, 0.43, 0.56, 1.76, 0.01, 0.12, 0.45, 1};
            //seriesCollection.Add(new LineSeries() { Title = "绫小路", Values = new ChartValues<double>(scoreList_1), DataLabels = false });
            
            cartesianChart.Series = seriesCollection;
        }

        private void SetChartFormat()
        {
            List<string> date = new List<string>();
            foreach (var dicVal in Auxiliarymethods.Instance.studentDatas_1[2].scoreArr)
                date.Add(dicVal[0].Split(' ')[0]);


            cartesianChart.AxisX.Add(new Axis
            {
                Title = "Examination",
                Labels = date,
            });

            cartesianChart.AxisY.Add(new Axis
            {
                Title = "Percentage of Score"
            });
            cartesianChart.LegendLocation = LegendLocation.Right;
        }

        int displayDataLenth = 0;
        int displayIndex = 0;
        private void ReDrawChart(int displayLenth,int startIndex,List<StudentData> studentData)
        {
            if (displayDataLenth == 0)
                return;

            cartesianChart.Series.Clear();
            SeriesCollection seriesCollection = new SeriesCollection();

            //if (displayIndex + displayDataLenth < studentData.Count) { }

            for (int i = startIndex; i < displayLenth; i++)
            {
                if (i >= studentData.Count)
                    return;

                List<double> scoreList = new List<double>();
                string name = studentData[i].Name;

                foreach (var dicVal in studentData[i].scoreArr)
                    scoreList.Add(double.Parse(dicVal[1]));

                seriesCollection.Add(new LineSeries() { Title = name, Values = new ChartValues<double>(scoreList), DataLabels = false });

                displayIndex = i + 1;
            }

            cartesianChart.Series = seriesCollection;           

        }

       
        private void displayDataLenthComboBox_SelectedIndexChanged(object sender, EventArgs e)//在启动时，这里会执行一次；
        {
            displayDataLenth = 0;
            displayIndex = 0;

            if ((string)displayDataLenthComboBox.SelectedItem != "All")
                displayDataLenth = int.Parse((string)displayDataLenthComboBox.SelectedItem);
            else
                displayDataLenth = Auxiliarymethods.Instance.studentDatas_1.Count;
            
        }

        private void scoreFluctuationComboBox_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void redrawChartButton_Click(object sender, EventArgs e)//下一组 按钮；
        {
            ReDrawChart(displayDataLenth, displayIndex, Auxiliarymethods.Instance.studentDatas_1);
        }
    }
}
