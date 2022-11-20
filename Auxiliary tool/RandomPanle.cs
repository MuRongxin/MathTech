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
        private int classStatus = 1;
        public RandomPanle()
        {
            InitializeComponent();
        }

        private void RandomPanle_Load(object sender, EventArgs e)
        {
            //randomTimer.Start();
            //changeColortimer.Start();
        }

        Color color1, color2, color3;Random random= new Random();   
        private void randomTimer_Tick(object sender, EventArgs e)
        {
            if (classStatus == 1)
                resoultLabel.Text = Auxiliarymethods.Instance.GetRandomResoult(Auxiliarymethods.Instance.dataList_1);
            else
                resoultLabel.Text = Auxiliarymethods.Instance.GetRandomResoult(Auxiliarymethods.Instance.dataList_2);


            int x = random.Next(550);
            int y = random.Next(200);
            resoultLabel.Location = new Point(x,y);
          

        }

        private void changeColortimer_Tick(object sender, EventArgs e)
        {
            Auxiliarymethods.Instance.ChangepanelColor(panel3, color1, out color1);
            Auxiliarymethods.Instance.ChangepanelColor(panel2, color2, out color2);
            Auxiliarymethods.Instance.ChangepanelColor(panel5, color3, out color3);
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
                if (classStatus == 1)
                    Auxiliarymethods.Instance.dataList_1.Remove(resoultLabel.Text);
                else
                    Auxiliarymethods.Instance.dataList_2.Remove(resoultLabel.Text);
            }
        }

        private void radioButton1_CheckedChanged(object sender, EventArgs e)
        {
            classStatus = 1;
        }

        private void radioButton2_CheckedChanged(object sender, EventArgs e)
        {
            classStatus = 2;
        }
    }
}
