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
            cartesianChart.Series.Clear();
            SeriesCollection seriesCollection = new SeriesCollection();
            List<int> temp = new List<int>() { 1, 2, 10, 3, 4, 4, 5, 8, 1, 0 };
            List<int> temp2 = new List<int>() { 2, 5, 7, 3, 9, 1, 2, 8, 2, 10 };
            seriesCollection.Add(new LineSeries() { Title = "绫小路", DataLabels = true, Values = new ChartValues<int>(temp) });
            seriesCollection.Add(new LineSeries() { Title = "砂糖", Values = new ChartValues<int>(temp2), DataLabels = true });
            cartesianChart.Series = seriesCollection;
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
