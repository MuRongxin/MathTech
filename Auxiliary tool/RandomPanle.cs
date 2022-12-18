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
            
            panelsList = Auxiliarymethods.Instance.GetControlChildControl(panel2);//获取panel2里面的所有子节点；

        }

       
        Random random= new Random(); 
        
        private void randomTimer_Tick(object sender, EventArgs e)
        {
            int ran = random.Next(Auxiliarymethods.Instance.studentDatas.Count);
            StudentData studentData = Auxiliarymethods.Instance.studentDatas[ran];
            resoultLabel.Text = studentData.Name + " " + studentData.ID;


            int x = random.Next(550);
            int y = random.Next(200);
            resoultLabel.Location = new Point(x,y);          

        }


        List<Control> panelsList = new List<Control>();     
        private void InitNameList()
        {      
            
            

            foreach (var item in panelsList)
            {
                item.ForeColor = Color.White;
            }
        }

       
      
        
        private void changeColortimer_Tick(object sender, EventArgs e)
        {
            panel3.BackColor = Auxiliarymethods.Instance.SmoothChangeColor(panel3.BackColor, "panel3.BackColor");
            panel2.BackColor = Auxiliarymethods.Instance.SmoothChangeColor(panel2.BackColor, "panel2.BackColor");
           
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
