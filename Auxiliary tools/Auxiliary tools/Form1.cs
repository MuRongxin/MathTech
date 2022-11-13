using System.Xml;
using System.Runtime.InteropServices;

namespace Auxiliary_tools
{
    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
            //ReadData();
            ReadData("./data43.txt"); 
            this.Text=String.Empty;
            this.ControlBox = false;
           
            this.MaximizedBounds = Screen.FromHandle(this.Handle).WorkingArea;
        }

        [DllImport("user32.dll", EntryPoint = "ReleaseCapture")]
        private extern static  void ReleaseCapture();
        [DllImport("user32.dll", EntryPoint = "SendMessage")]
        private extern static  void SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
        private void button2_Click(object sender, EventArgs e)
        {
            Environment.Exit(0);
        }

        private void title_Click(object sender, EventArgs e)
        {

        }

        private void content_Paint(object sender, PaintEventArgs e)
        {

        }

        private void treeView1_AfterSelect(object sender, TreeViewEventArgs e)
        {

        }

        private void treeView1_AfterSelect_1(object sender, TreeViewEventArgs e)
        {

        }

        private void panel4_Paint(object sender, PaintEventArgs e)
        {

        }

        private void drawer_Paint(object sender, PaintEventArgs e)
        {

        }

        bool isDrawer=true;
        /// <summary>
        /// 负责面板动画
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void timer_Tick(object sender, EventArgs e)//
        {
            
            if (isDrawer)
            {
                drawer.Width -= 10;
                home_button.Width -= 10;
                setting_button.Width-=10;
                about_button.Width-=10;
                if (drawer.Width == drawer.MinimumSize.Width)
                {
                    isDrawer = false;
                    timer.Stop();
                }
            }
            else
            {
                drawer.Width += 10;
                home_button.Width += 10;
                setting_button.Width += 10;
                about_button.Width += 10;
                if (drawer.Width == drawer.MaximumSize.Width)
                {
                    isDrawer = true;   
                    timer.Stop();
                }

            }
            //content_1.Text = drawer.Width.ToString();
        }

        private void menuButton_Click(object sender, EventArgs e)
        {
            timer.Start();
        }

        /// <summary>
        /// 储存读取到的名单；
        /// </summary>
        private string[] dataArray = { "10101_早川秋","21022_电次","3203203_林克","","4343434_椎名真白" };
        Random random=new Random();
       
        private void start_button_Click(object sender, EventArgs e)
        {
            if (start_button.Text== "Start Random")
            {
                start_button.Text = "Stop Random";
                random_timer.Start();
            }
            else
            {
                start_button.Text = "Start Random";
                random_timer.Stop();
            }

            //ReadData();
            //往结果面板里面添加文本；
            if (start_button.Text == "Start Random")
            {
                resoulrTextBox.Text += content_1.Text + "\n";
            }
            //Test_out.BackColor = ThemeColor.RandomColor();
            //Test_out.Text = Test_out.BackColor.ToString();
        }

        private void random_timer_Tick(object sender, EventArgs e)
        {
            int temp = random.Next(dataArray.Length);
            content_1.Text=dataArray[temp];//将结果文本设置给 content_1 Text 组件；

            Test_out.BackColor = ThemeColor.RandomColor();
            Test_out.Text = Test_out.BackColor.ToString();
        }

        List<string> data = new List<string>();
        /// <summary>
        /// 对于xml文档的读取；
        /// </summary>
        private void ReadData()
        {
            string number = "";
            string name = "";
            XmlDocument xmlDocument = new XmlDocument();
            xmlDocument.Load(".\\data.xml");

            XmlNodeList xmlNodeList = xmlDocument.SelectSingleNode("root").ChildNodes;
           // List<string> data = new List<string>();
            foreach (XmlNode childNode in xmlNodeList)
            {
                XmlElement childElement = (XmlElement)childNode;
                //if (xmlElement.GetAttributeNode("id") == null)
                //    continue;

                //int id = Convert.ToInt32(xmlElement.GetAttributeNode("id"));

                foreach (XmlNode cchildNode in childNode.ChildNodes)
                {
                    XmlElement element= (XmlElement)cchildNode;
                    switch (element.Name)
                    {
                        case "number":
                            number = element.InnerText;
                            break;
                        case "name":
                            name = element.InnerText;
                            break;
                        default:
                            break;
                    }
                    //number = element.Item(0).InnerText;
                    //name=element.Item(1).InnerText;

                   
                }
                data.Add(number + "_" + name);
            }
            //string temp = "";
            //foreach (var item in data)
            //{
            //    temp += item;
            //}
            //temp_label.Text=temp;

        }

        private void ReadData(string path)
        {
            dataArray = File.ReadAllLines(path);
            temp_label.Text = "班级数据长度：" + dataArray.Length.ToString();
        }

        /// <summary>
        /// 点击班级按钮，重写dataArray数据；
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void radioButton2_CheckedChanged(object sender, EventArgs e)
        {
            content_1.Text = "";
            resoulrTextBox.Clear();
            ReadData("./data2.txt");
        }
        
        private void radioButton1_CheckedChanged(object sender, EventArgs e)
        {
            content_1.Text = "";
            resoulrTextBox.Clear();
            ReadData("./data43.txt");

        }

        private void panel2_Paint(object sender, PaintEventArgs e)
        {
            
        }

        private void panel2_MouseDown(object sender, MouseEventArgs e)
        {
            ReleaseCapture();
            SendMessage(this.Handle, 0x112, (IntPtr)0xf012, (IntPtr)0);
        }

        private void maximize_button_Click(object sender, EventArgs e)
        {
            if (WindowState == FormWindowState.Normal)
                this.WindowState = FormWindowState.Maximized;
            else
                this.WindowState = FormWindowState.Normal;
        }
    }
}