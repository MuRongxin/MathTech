using LiveCharts;
using LiveCharts.Defaults;
using LiveCharts.Wpf;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Auxiliary_tool
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }
        [DllImport("user32.dll", EntryPoint = "ReleaseCapture")]
        private extern static void ReleaseCapture();
        [DllImport("user32.dll", EntryPoint = "SendMessage")]
        private extern static void SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);

        private static Form1 _obj;
        public static Form1 Instance
        {
            get {
                if (_obj == null) 
                    _obj = new Form1();

                return _obj;               
            }           
        }

        public Panel PanelContainer
        {
            get{ return overview_pane; }
            set { overview_pane = value; }
        }

        private void label1_Click(object sender, EventArgs e)
        {

        }

        private void guna2Button1_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            InitChart();
            _obj = this;

            InitData();

            //RandomPanle randomPanle = new RandomPanle();
            //randomPanle.Dock = DockStyle.Fill;

            //Score_Analysis_Panle score_Analysis = new Score_Analysis_Panle();
            //score_Analysis.Dock = DockStyle.Fill;

            //PanelContainer.Controls.Add(randomPanle);
            //PanelContainer.Controls.Add(score_Analysis);

            rushTimer.Start();
           
        }
        private void InitData()
        {

            Auxiliarymethods.Instance.ReadDataXml("./data43.xml",Auxiliarymethods.Instance.studentDatas_1);
            Auxiliarymethods.Instance.ReadDataXml("./data45.xml", Auxiliarymethods.Instance.studentDatas_2);

            Auxiliarymethods.Instance.ReadExcel("./Exam143Score.xlsx",Auxiliarymethods.Instance.studentDatas_1);
            Auxiliarymethods.Instance.ReadExcel("./Exam145Score.xlsx", Auxiliarymethods.Instance.studentDatas_2);


            datalengthLabel1.Text = Auxiliarymethods.Instance.studentDatas_1.Count.ToString();
            datalengthLabel2.Text = Auxiliarymethods.Instance.studentDatas_2.Count.ToString();

            overview_pane.Select();//设置默认焦点；
        }

        private bool isInitPanel;
        private void InitPanel()
        {
            RandomPanle randomPanle = new RandomPanle();
            randomPanle.Dock = DockStyle.Fill;

            Score_Analysis_Panle score_Analysis = new Score_Analysis_Panle();
            score_Analysis.Dock = DockStyle.Fill;

            PanelContainer.Controls.Add(randomPanle);
            PanelContainer.Controls.Add(score_Analysis);
        }

        private void DropWindow(object sender, MouseEventArgs e)
        {
            ReleaseCapture();
            SendMessage(this.Handle, 0x112, (IntPtr)0xf012, (IntPtr)0);
        }

        /// <summary>
        /// 切换随机界面
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void switchRandomPanel_Click(object sender, EventArgs e)
        {
            if (!isInitPanel) { 
                MessageBox.Show("请先选择执教班级", "注意", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;}

            Dataview_panel.Visible = false;
            ChartView_Panel.Visible = false;
            PanelContainer.Controls["RandomPanle"].Visible = true;
            PanelContainer.Controls["Score_Analysis_Panle"].Visible = false;
            PanelContainer.Controls["RandomPanle"].BringToFront();
        }

        /// <summary>
        /// 切换主界面
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void switchMainpanelButton_Click_1(object sender, EventArgs e)
        {
            if (!isInitPanel)
            {
                MessageBox.Show("请先选择执教班级", "注意", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }
            Dataview_panel.Visible = true; 
            ChartView_Panel.Visible = true;
            PanelContainer.Controls["RandomPanle"].Visible=false;
            PanelContainer.Controls["Score_Analysis_Panle"].Visible = false;
        }
        /// <summary>
        /// 切换成绩分析界面
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void switchScoreAnalysePanelButton2_Click(object sender, EventArgs e)
        {
            if (!isInitPanel) {
                MessageBox.Show("请先选择执教班级","注意", MessageBoxButtons.OK,MessageBoxIcon.Warning);
                return; }
            Dataview_panel.Visible = false;
            ChartView_Panel.Visible = false;
            PanelContainer.Controls["Score_Analysis_Panle"].Visible = true;
            PanelContainer.Controls["Score_Analysis_Panle"].BringToFront();
            
        }

        private void InitChart()
        {
            average_CartesianChart.Series = new SeriesCollection
            {
                new LineSeries
                {
                    Values =new ChartValues<ObservablePoint>
                    {
                        new ObservablePoint(1,10),
                        new ObservablePoint(3,2.1),
                         new ObservablePoint(5,5),
                        new ObservablePoint(10,8),
                    },
                    PointGeometrySize=11
                },
                 new LineSeries
                {
                    Values =new ChartValues<ObservablePoint>
                    {
                        new ObservablePoint(1,5),
                        new ObservablePoint(2,6),
                         new ObservablePoint(3,4),
                        new ObservablePoint(8,6),
                    },
                    PointGeometrySize=11              
                 
                },
            };
        }

        private void rushTimer_Tick(object sender, EventArgs e)
        {
            TimeLabel.Text = DateTime.Now.ToString();
        }

        private void minimizeButton_Click(object sender, EventArgs e)
        {
            this.WindowState = FormWindowState.Minimized;
        }

        private void Dataview_panel_Paint(object sender, PaintEventArgs e)
        {
           
        }       
       

        private void searchTextBox_TextChanged(object sender, EventArgs e)
        {
            MessageBox.Show("这是提示框中的文本", "提示框标题", MessageBoxButtons.OKCancel, MessageBoxIcon.Warning);
        }

        private void searchTextBox_KeyDown(object sender, KeyEventArgs e)
        {
            if (e.KeyCode==Keys.Enter)
            {
                MessageBox.Show(searchTextBox.Text, "提示框标题", MessageBoxButtons.OKCancel, MessageBoxIcon.Warning);
            }
        }

        private void searchTextBox_Leave(object sender, EventArgs e)
        {
            MessageBox.Show(searchTextBox.Text, "提示框标题", MessageBoxButtons.OKCancel, MessageBoxIcon.Warning);
        }

        int currnetClass = 0;

        private void select43Button_Click(object sender, EventArgs e)
        {
            if (!isInitPanel) 
            {
                Auxiliarymethods.Instance.studentDatas = Auxiliarymethods.Instance.studentDatas_1;
                InitPanel();
                isInitPanel = true;
            }
            class43InfoPanel.Visible=true;
            smoothChangeTimer.Start();
            currnetClass = 1;
            Auxiliarymethods.Instance.studentDatas = Auxiliarymethods.Instance.studentDatas_1;
        }

        private void select45Button_Click(object sender, EventArgs e)
        {
            if (!isInitPanel)
            {
                Auxiliarymethods.Instance.studentDatas = Auxiliarymethods.Instance.studentDatas_2;
                InitPanel();
                isInitPanel = true;
            }
            Auxiliarymethods.Instance.studentDatas = Auxiliarymethods.Instance.studentDatas_2;

            if (class45InfoPanel.Width==0|| class45InfoPanel.Width>=tagetwith-19)
                class45InfoPanel.Location = new Point(774, class45InfoPanel.Location.Y);
            if ( class45InfoPanel.Width >= tagetwith - 19)
                class45InfoPanel.Location = new Point(78, class45InfoPanel.Location.Y);

            class45InfoPanel.Visible = true;
            smoothChangeTimer.Start();
            currnetClass = 2;
        }

        int range = 25; int tagetwith = 696;
        private void smoothChangeTimer_Tick(object sender, EventArgs e)
        {
            if (currnetClass == 1)
            {                 
                if (class43InfoPanel.Size.Width >= tagetwith)
                {
                    smoothChangeTimer.Stop();
                    class45InfoPanel.Visible = false;
                }

                class43InfoPanel.Size = new Size(Auxiliarymethods.Instance.SmoothChangeValue(class43InfoPanel.Width, tagetwith, range), class43InfoPanel.Size.Height);
                                
                if(class45InfoPanel.Width>0)
                    class45InfoPanel.Location = new Point(class45InfoPanel.Location.X + range, class45InfoPanel.Location.Y);

                class45InfoPanel.Width -= range;             

            }
            else
            {
               
                class45InfoPanel.Width = Auxiliarymethods.Instance.SmoothChangeValue(class45InfoPanel.Width, tagetwith, range);
                class45InfoPanel.Location = new Point(class45InfoPanel.Location.X - range, class45InfoPanel.Location.Y);

                class43InfoPanel.Width -= range;

                 if (class45InfoPanel.Size.Width >= tagetwith) 
                { 
                    smoothChangeTimer.Stop();
                    class43InfoPanel.Visible = false;
                }
            }
        }

       
    }
}
