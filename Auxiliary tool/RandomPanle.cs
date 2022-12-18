using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Auxiliary_tool
{
    public partial class RandomPanle : UserControl
    {
        private List<string> nameList=new List<string>();
        public RandomPanle()
        {
            InitializeComponent();
        }



        private void RandomPanle_Load(object sender, EventArgs e)
        {
            InitNameList();
        }

        Color color1, color2, color3;
        Random random= new Random(); 
        
        private void randomTimer_Tick(object sender, EventArgs e)
        {
            resoultLabel.Text = Auxiliarymethods.Instance.GetRandomResoult(nameList);   

            int x = random.Next(550);
            int y = random.Next(200);
            resoultLabel.Location = new Point(x,y);          

        }

        private void InitNameList()
        {
            nameList.Clear();
            foreach (var item in Auxiliarymethods.Instance.studentDatas)
            {
                nameList.Add(item.Name);
            }

            GetChildControl(panel2);
            foreach (var item in panelsList)
            {
                item.ForeColor = Color.White;
            }
        }

        List<Control> panelsList = new List<Control>();
        
        /// <summary>
        /// 递归获得所有子控件
        /// </summary>
        /// <param name="panel"></param>
        private void GetChildControl(Control panel)
        {
            if (panel.Controls.Count == 0)
                return;

            for (int i = 0; i < panel.Controls.Count; i++)
            {
                panelsList.Add(panel.Controls[i]);
                GetChildControl(panel.Controls[i]);
            }           
        }
        
        private void changeColortimer_Tick(object sender, EventArgs e)
        {
            Auxiliarymethods.Instance.ChangepanelColor(panel3, color1, out color1);
            Auxiliarymethods.Instance.ChangepanelColor(panel2, color2, out color2);
            //Auxiliarymethods.Instance.ChangepanelColor(panel5, color3, out color3);

            startRandomButton.BackColor = Auxiliarymethods.Instance.SmoothChangeColor(startRandomButton.BackColor, "startRandomButton");
            startRandomButton.ForeColor = Auxiliarymethods.Instance.SmoothChangeColor(startRandomButton.ForeColor, "startRandomButtonForeColor");
         
            for (int i = 0; i < panelsList.Count; i++)
            {
                panelsList[i].BackColor = Auxiliarymethods.Instance.SmoothChangeColor(panelsList[i].BackColor, panelsList[i].Name);               
            }
        }

        private void startRandomButton_Click(object sender, EventArgs e)
        {
            if (startRandomButton.Text == "Start Random")
            {
                startRandomButton.Text = "Stop Random";
                randomTimer.Start();
                changeColortimer.Start();
            }
            else
            {
                startRandomButton.Text = "Start Random";
                randomTimer.Stop();
                changeColortimer.Stop();

            }

            if (startRandomButton.Text == "Start Random")
            {
                
            }
        }

    }
}
