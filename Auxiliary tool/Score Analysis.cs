﻿using System;
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

            displayDataLenthComboBox.SelectedIndex = 0;//默认显示的数据量；

            SetChartFormat();

            InitDropdownlist();
            

            InitDrawChartData(currentStudentDataList);

            //FirstChart();
        }

        public void StartThisPanle()
        {
            currentStudentDataList = Auxiliarymethods.Instance.studentDatas;
            FirstChart();
            InitDropdownlist();
        }
        private void charttestButton_Click(object sender, EventArgs e)
        {
            //InitDrawChartData(Auxiliarymethods.Instance.studentDatas_1);

        }

        Dictionary<string, List<double>> scoreDic = new Dictionary<string, List<double>>();

        List<StudentData> currentStudentDataList = new List<StudentData>();

        private void InitDrawChartData(List<StudentData> studentDatas)
        {
            cartesianChart.Series.Clear();            

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

        private void SetChartFormat()
        {
            List<string> date = new List<string>();
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
        private void ReDrawChart(int displayLenth,int startIndex, List<StudentData> studentData, bool isClearSeries = true)
        {
            if (displayLenth == 0)
                return;

            if (isClearSeries)
                cartesianChart.Series.Clear();

            SeriesCollection seriesCollection = new SeriesCollection();


            for (int i = startIndex; i < startIndex+displayLenth; i++)
            {
                if (i >= studentData.Count)
                    break;

                List<double> scoreList = new List<double>();
                string name = studentData[i].Name;

                foreach (var dicVal in studentData[i].scoreArr)
                    scoreList.Add(double.Parse(dicVal[1]));

                seriesCollection.Add(new LineSeries() { Title = name, Values = new ChartValues<double>(scoreList), DataLabels = false });

                displayIndex = i + 1;
            }

            foreach (var item in cartesianChart.Series)//如果需要的话，在原有的基础上添加图表数据；
            {
                seriesCollection.Add(item);
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
                displayDataLenth = currentStudentDataList.Count;
            
        }

        private void scoreFluctuationComboBox_SelectedIndexChanged(object sender, EventArgs e)
        {

        }

        private void redrawChartButton_Click(object sender, EventArgs e)//下一组 按钮；
        {
            ReDrawChart(displayDataLenth, displayIndex, currentStudentDataList);
           
        }

        private void InitDropdownlist()
        {
            selectStuComboBox.Items.Clear();
            foreach (var item in currentStudentDataList)
            {
                
                selectStuComboBox.Items.Add(item.Name);
                comboBox1.Items.Add(item.Name);//暂时的;
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
                int startIndex=random.Next(currentStudentDataList.Count);

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

                ReDrawChart(1, startIndex, currentStudentDataList,false);
                randomNumlist.Add(startIndex);
            }
           
        }
    }
}
