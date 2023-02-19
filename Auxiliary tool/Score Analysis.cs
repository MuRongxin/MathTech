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
        private static Score_Analysis_Panle _obj;
        public static Score_Analysis_Panle Instance
        {
            get
            {
                if (_obj == null)
                    _obj = new Score_Analysis_Panle();

                return _obj;
            }
        }

        public Score_Analysis_Panle()
        {
            InitializeComponent();
        }

        private void Score_Analysis_Load(object sender, EventArgs e)
        {
            _obj = this;

            currentStudentDataList = Auxiliarymethods.Instance.studentDatas;


            SetChartFormat();

            InitDropdownlist();


            InitDrawChartData(currentStudentDataList);

            //FirstChart();
        }

        public void StartThisPanle()
        {
            currentStudentDataList = Auxiliarymethods.Instance.studentDatas;
            InitDrawChartData(currentStudentDataList);
            FirstChart();
            InitDropdownlist();
        }
        private void charttestButton_Click(object sender, EventArgs e)//清除所有 数据图；
        {
            //InitDrawChartData(Auxiliarymethods.Instance.studentDatas_1);
            cartesianChart.Series.Clear();
            directSelectStudentBox.SelectedItem = null;
        }

        Dictionary<string, List<double>> scoreDic = new Dictionary<string, List<double>>();

        List<StudentData> currentStudentDataList = new List<StudentData>();

        private void InitDrawChartData(List<StudentData> studentDatas)
        {
            cartesianChart.Series.Clear();
            scoreDic.Clear();

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
                //seriesCollection.Add(new LineSeries() { Title = name, Values = new ChartValues<double>(scoreList), DataLabels = false });
            }
            //List<double> scoreList_1 = new List<double>() { 0.11, 0.21, 0.41, 0.21, 0.43, 0.56, 1.76, 0.01, 0.12, 0.45, 1};
            //seriesCollection.Add(new LineSeries() { Title = "绫小路", Values = new ChartValues<double>(scoreList_1), DataLabels = false });

            //cartesianChart.Series = seriesCollection;
        }

        List<string> date = new List<string>();
        private void SetChartFormat()
        {
            cartesianChart.AxisX.Clear();
            cartesianChart.AxisY.Clear();
            date.Clear();

            foreach (var dicVal in currentStudentDataList[2].scoreArr)
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
        private void ReDrawChart(int displayLenth, int startIndex, List<StudentData> studentData, bool isClearSeries = true, bool isOnlyRedrawLastWeek = false)
        {
            if (displayLenth == 0)
                return;

            if (isClearSeries)
                cartesianChart.Series.Clear();

            SeriesCollection seriesCollection = new SeriesCollection();


            for (int i = startIndex; i < startIndex + displayLenth; i++)
            {
                if (i >= studentData.Count)
                    break;

                List<double> scoreList = new List<double>();
                string name = studentData[i].Name;

                foreach (var dicVal in studentData[i].scoreArr)
                    scoreList.Add(double.Parse(dicVal[1]));

                if (isOnlyRedrawLastWeek)
                {
                    scoreList = scoreList.GetRange(scoreList.Count - 7, 7);
                }
                seriesCollection.Add(new LineSeries() { Title = name, Values = new ChartValues<double>(scoreList), DataLabels = false });

                displayIndex = i + 1;
            }

            foreach (var item in cartesianChart.Series)//如果需要的话，在原有的基础上添加图表数据；
            {
                seriesCollection.Add(item);
            }

            cartesianChart.Series = seriesCollection;

        }


        private void displayDataLenthComboBox_SelectedIndexChanged(object sender, EventArgs e)//选择数据量下拉框，在启动时，这里会执行一次；
        {
            displayDataLenth = 0;
            displayIndex = 0;

            if ((string)displayDataLenthComboBox.SelectedItem != "All")
                displayDataLenth = int.Parse((string)displayDataLenthComboBox.SelectedItem);
            else
                displayDataLenth = currentStudentDataList.Count;

        }

        private void DirectSelectStudentComboBox_SelectedIndexChanged(object sender, EventArgs e)//直接选择学生下拉框；
        {
            if (directSelectStudentBox.SelectedItem == null)
                return;
            string name = directSelectStudentBox.SelectedItem.ToString();

            DirectSelectStudent(name);
        }

        private void RedrawChartButton_Click(object sender, EventArgs e)//下一组 按钮；
        {
            if (isOnlyRedrawLastweek)
            {
                ReDrawChart(displayDataLenth, displayIndex, currentStudentDataList, isOnlyRedrawLastWeek: true);
                return;
            }

            ReDrawChart(displayDataLenth, displayIndex, currentStudentDataList);
        }

        private void InitDropdownlist()
        {
            directSelectStudentBox.Items.Clear();
            foreach (var item in currentStudentDataList)
            {
                directSelectStudentBox.Items.Add(item.Name);
            }
        }

        private void FirstChart()
        {
            cartesianChart.Series.Clear();

            Random random = new Random();
            int count = random.Next(3, 7);
            List<int> randomNumlist = new List<int>();
            bool isRepeat = false;
            for (int i = 0; i < count; i++)
            {
                int startIndex = random.Next(currentStudentDataList.Count);

                foreach (var item in randomNumlist)//校验随机开始的index是否出现重复；
                    if (startIndex == item)
                    {
                        isRepeat = true;
                        break;
                    }

                if (isRepeat)
                {
                    isRepeat = false;
                    break;
                }

                ReDrawChart(1, startIndex, currentStudentDataList, false);
                randomNumlist.Add(startIndex);
            }

        }

        /// <summary>
        /// 通过下拉框直接选择学生
        /// </summary>
        private void DirectSelectStudent(string name)
        {
            SeriesCollection seriesCollection = cartesianChart.Series;

            if (isOnlyRedrawLastweek)
                seriesCollection.Add(new LineSeries() { Title = name, Values = new ChartValues<double>(scoreDic[name].GetRange(scoreDic[name].Count - 7, 7)), DataLabels = false });
            else
                seriesCollection.Add(new LineSeries() { Title = name, Values = new ChartValues<double>(scoreDic[name]), DataLabels = false });

            cartesianChart.Series = seriesCollection;
        }

        private void ClearChartButton_Click(object sender, EventArgs e)
        {
            cartesianChart.Series.Clear();
            directSelectStudentBox.SelectedItem = null;
        }

        SeriesCollection oriSeries = new SeriesCollection();
        private void lastWeekScoreButton_Click(object sender, EventArgs e)
        {
            if (lastWeekScoreButton.Text == "Last 7 days")
            {
                isOnlyRedrawLastweek = true;
                foreach (var item in cartesianChart.Series)
                {
                    oriSeries.Add(new LineSeries() { Title = item.Title, Values = new ChartValues<double>((ChartValues<double>)item.Values) });
                }

                CheckLastWeekScore();
                lastWeekScoreButton.Text = "All";

                List<string> lastWeekdate = date.GetRange(date.Count - 7, 7);

                cartesianChart.AxisX.Clear();
                cartesianChart.AxisX.Add(new Axis
                {
                    Title = "Examination",
                    Labels = lastWeekdate,
                });

            }
            else
            {
                isOnlyRedrawLastweek = false;
                lastWeekScoreButton.Text = "Last 7 days";

                cartesianChart.AxisX.Clear();
                cartesianChart.AxisX.Add(new Axis
                {
                    Title = "Examination",
                    Labels = date,
                });

                RecoverAllScore();
            }
        }

        private void RecoverAllScore()
        {
            cartesianChart.Series = oriSeries;
            //oriSeries.Clear();
        }

        bool isOnlyRedrawLastweek;
        private void CheckLastWeekScore()
        {
            if (Auxiliarymethods.Instance.studentDatas[0].scoreArr.Count < 7)
            {
                MessageBox.Show("当前成绩数量小于7，无法筛选", "警告", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }

            SeriesCollection series = new SeriesCollection();
            Dictionary<string, ChartValues<double>> scoreDic = new Dictionary<string, ChartValues<double>>();

            foreach (Series item in cartesianChart.Series)
            {
                if (!scoreDic.ContainsKey(item.Title))
                    scoreDic.Add(item.Title, (ChartValues<double>)item.Values);
            }

            foreach (var item in scoreDic)
            {

                var currentScoreList = scoreDic[item.Key].ToList();
                if (isOnlyRedrawLastweek)
                    series.Add(new LineSeries() { Title = item.Key, Values = new ChartValues<double>(currentScoreList.GetRange(currentScoreList.Count - 7, 7)) });

            }

            cartesianChart.Series.Clear();
            cartesianChart.Series = series;

        }

        private void Half_score_Click(object sender, EventArgs e)
        {
            if (Auxiliarymethods.Instance.currnetClass == 1)
                currentStudentDataList = Auxiliarymethods.Instance.studentDatas_1;
            if (Auxiliarymethods.Instance.currnetClass == 2)
                currentStudentDataList = Auxiliarymethods.Instance.studentDatas_2;

            cartesianChart.Series.Clear();
           
            SetChartFormat();
            FirstChart();
        }

        private void all_score_Click(object sender, EventArgs e)
        {
            if (Auxiliarymethods.Instance.currnetClass == 1)
                currentStudentDataList = Auxiliarymethods.Instance.studentDatas_1_2;
            if (Auxiliarymethods.Instance.currnetClass == 2)
                currentStudentDataList = Auxiliarymethods.Instance.studentDatas_2_2;

            cartesianChart.Series.Clear();
         
            SetChartFormat();
            FirstChart();
        }
    }
}
