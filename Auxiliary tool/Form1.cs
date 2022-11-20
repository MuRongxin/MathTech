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
            average_CartesianChart = new LiveCharts.WinForms.CartesianChart();
            _obj = this;

            RandomPanle randomPanle = new RandomPanle();
            randomPanle.Dock = DockStyle.Fill; 
            PanelContainer.Controls.Add(randomPanle);

            InitData();
        }
        private void InitData()
        {
            Auxiliarymethods.Instance.ReadData();
            datalengthLabel1.Text = Auxiliarymethods.Instance.dataList_1.Count.ToString();
            datalengthLabel2.Text = Auxiliarymethods.Instance.dataList_2.Count.ToString();
        }
                

        private void DropWindow(object sender, MouseEventArgs e)
        {
            ReleaseCapture();
            SendMessage(this.Handle, 0x112, (IntPtr)0xf012, (IntPtr)0);
        }

        private void randomPanelswitchButton3_Click(object sender, EventArgs e)
        {
            // overview_pane.Visible = false;

            //Dataview_panel

            Dataview_panel.Visible = false;
            ChartView_Panel.Visible = false;
            PanelContainer.Controls["RandomPanle"].Visible = true;
            PanelContainer.Controls["RandomPanle"].BringToFront();
        }

        private void guna2Button1_Click_1(object sender, EventArgs e)
        {
            Dataview_panel.Visible = true;
            ChartView_Panel.Visible = true;
            PanelContainer.Controls["RandomPanle"].Visible=false;   
        }
    }
}
