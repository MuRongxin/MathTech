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
        
        public RandomPanle()
        {
            InitializeComponent();
        }



        private void RandomPanle_Load(object sender, EventArgs e)
        {
            
            panelsList = Auxiliarymethods.Instance.GetControlChildControl(panel2);//获取panel2里面的所有子节点；
            
        }

       
        Random random= new Random();
        StudentData studentData;
        private void randomTimer_Tick(object sender, EventArgs e)
        {
            int rang = random.Next(Auxiliarymethods.Instance.studentDatas.Count);
            //studentData = Auxiliarymethods.Instance.studentDatas[rang];
            resoultLabel.Text = Auxiliarymethods.Instance.studentDatas[rang].Name;


            int x = random.Next(550);
            int y = random.Next(200);
            resoultLabel.Location = new Point(x,y);        

        }

        private List<StudentData> resoultList = new List<StudentData>();
       
        private void GetRandomResoult()
        {
            while (true)
            {
                bool isIdentical = false;
                int rang = random.Next(Auxiliarymethods.Instance.studentDatas.Count);
                studentData = Auxiliarymethods.Instance.studentDatas[rang];

                foreach (var item in resoultList)
                {
                    if (item == studentData)
                    {
                        isIdentical = true;
                        break;
                    }
                }

                if (!isIdentical)
                    break;

            }
            resoultList.Add(studentData);
            resoultLabel.Text = studentData.Name;

        }

        List<Control> panelsList = new List<Control>();     
        private void Initpanel()
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

                GetRandomResoult();

                SetResoultTexBox(studentData.Name, studentData.CallCount.ToString());

                randomTimer.Stop();
                changeColortimer.Stop();

            }

            if (startRandomButton.Text == "Start Random")
            {
                
            }
        }

        private void SetResoultTexBox(string name, string callCount)
        {            
            List<string> res = new List<string>();
            if (richTextBox.Lines != null)
                res = richTextBox.Lines.ToList<string>();
            
            res.Insert(0," " + name + " " + "[" + callCount + "]");
            richTextBox.Lines = res.ToArray();

            richTextBox.Clear();
            foreach (var item in res)
            {
                richTextBox.SelectionColor = ThemeColor.RandomColor();
                richTextBox.AppendText(item + "\n");
            }

        }

    }
}
