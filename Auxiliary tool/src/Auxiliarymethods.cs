using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml;
using LiveCharts;
using LiveCharts.Defaults;
using LiveCharts.Wpf;
using ExcelDataReader;
using System.Data;
using System.Data.OleDb;

namespace Auxiliary_tool
{
    class Auxiliarymethods
    {
       
        public List<string> dataList_1 = new List<string>();
        public List<string> dataList_2 = new List<string>();

        public List<StudentData> studentDatas= new List<StudentData>();

        private static Auxiliarymethods _obj;
        public static Auxiliarymethods Instance
        {
            get
            {
                if (_obj == null)
                    _obj = new Auxiliarymethods();
                return _obj;
            }
        }       
        public string Getstring()
        {
            return "1234";
        }

        
        static List<string> colors = new List<string>() { };
        static Random random = new Random();
        public static Color RandomColor()
        {
            int color_1, color_2, color_3;

            color_1 = random.Next(256);
            color_2 = random.Next(256);
            color_3 = random.Next(256);
            string r_color = color_1.ToString("X2");
            string g_color = color_2.ToString("X2");
            string b_color = color_3.ToString("X2");

            return ColorTranslator.FromHtml("#" + r_color + g_color + b_color);
        }

        public void ReadData()
        {
            string[] dataArray = File.ReadAllLines("./data43.txt");
            dataList_1 = dataArray.ToList();
            string[] dataArray2 = File.ReadAllLines("./data45.txt");
            dataList_2 = dataArray2.ToList();
        }

        public string GetRandomResoult(List<string> data)
        {
            int temp = random.Next(data.Count);
            return data[temp];
        }

       
        public bool isChangeColor = true;
        int isChangetimer = 0;
        public void ChangepanelColor(Panel panel, Color falColor,out Color resColor)
        {
            if (isChangeColor)
            {
                falColor = ThemeColor.RandomColor();                
                isChangeColor = false;
            }
            isChangetimer++;
            //Test_out.Text = isChangetimer.ToString();
            if (isChangetimer >= 500)
            {
                isChangetimer = 0;
                isChangeColor = true;
            }
            Color resoult_1;
            SmoothChangeColor(panel.BackColor, falColor, out resoult_1);
            panel.BackColor = resoult_1;

            resColor = falColor;
        }

        private void SmoothChangeColor(Color oriColor, Color targetColor, out Color resoultColor)
        {
            Color tempColor = targetColor;

            if (targetColor.R > oriColor.R)
            {
                int temp = oriColor.R;
                temp++;
                tempColor = Color.FromArgb(temp, oriColor.G, oriColor.B);
            }
            if (targetColor.R < oriColor.R)
            {
                int temp = oriColor.R;
                temp--;
                tempColor = Color.FromArgb(temp, oriColor.G, oriColor.B);
            }
            if (targetColor.G > oriColor.G)
            {
                int temp = oriColor.G;
                temp++;
                tempColor = Color.FromArgb(oriColor.R, temp, oriColor.B);
            }
            if (targetColor.G < oriColor.G)
            {
                int temp = oriColor.G;
                temp--;
                tempColor = Color.FromArgb(oriColor.R, temp, oriColor.B);
            }
            if (targetColor.B > oriColor.B)
            {
                int temp = oriColor.B;
                temp++;
                tempColor = Color.FromArgb(oriColor.R, oriColor.G, temp);
            }
            if (targetColor.B < oriColor.B)
            {
                int temp = oriColor.B;
                temp--;
                tempColor = Color.FromArgb(oriColor.R, oriColor.G, temp);
            }

            resoultColor = tempColor;

        }

        private void ReadDataXml(string path)
        {
            string callCount = "";
            string name = "";
            XmlDocument xmlDocument = new XmlDocument();
            xmlDocument.Load(path);

            XmlNodeList xmlNodeList = xmlDocument.SelectSingleNode("root").ChildNodes;
            // List<string> data = new List<string>();
            foreach (XmlNode childNode in xmlNodeList)
            {
                XmlElement childElement = (XmlElement)childNode;
                if (childElement.GetAttributeNode("id") == null)
                    continue;

                int id = Convert.ToInt32(childElement.GetAttributeNode("id").Value);

                foreach (XmlNode cchildNode in childNode.ChildNodes)
                {
                    XmlElement element = (XmlElement)cchildNode;
                    switch (element.Name)
                    {
                        case "callCount":
                            callCount = element.InnerText;
                            break;
                        case "name":
                            name = element.InnerText;
                            break;
                        default:
                            break;
                    }
                }
                studentDatas.Add(new StudentData(id, name, int.Parse(callCount)));
            }           

        }
        
        /// <summary>
        /// 创建XML文件
        /// </summary>
        public void CreatXMLFile(string path, string[] dataArray)
        {

            XmlDocument xmlDocument = new XmlDocument();
            XmlDeclaration xmlDeclaration = xmlDocument.CreateXmlDeclaration("1.0", "UTF-8", "");
            xmlDocument.AppendChild(xmlDeclaration);


            List<string> oriData = dataArray.ToList<string>();

            //创建根节点
            XmlElement root = xmlDocument.CreateElement("root");

            foreach (var item in oriData)
            {
                string[] strtemp = item.Split(' ');
                //创建二级子节点
                XmlElement student = xmlDocument.CreateElement("student");
                student.SetAttribute("id", strtemp[0]);
                //创建三级子节点
                XmlElement name = xmlDocument.CreateElement("name");
                name.InnerText = strtemp[1];

                XmlElement callCount = xmlDocument.CreateElement("callCount");
                callCount.InnerText = "0";

                //设置节点父子关系
                root.AppendChild(student);
                student.AppendChild(name);
                student.AppendChild(callCount);
            }
            //添加根节点至xml文档
            xmlDocument.AppendChild(root);
            //创建
            xmlDocument.Save(path);
        }
        /// <summary>
        /// 更新节点数据
        /// </summary>
        /// <param name="path"></param>
        public void UpdataXmlData(string path)
        {
            XmlDocument xmlDocument = new XmlDocument();
            xmlDocument.Load(path);
            XmlNode root = xmlDocument.SelectSingleNode("root");
            XmlNodeList xmlNodeList = xmlDocument.SelectSingleNode("root").ChildNodes;

            //修改节点数值
            foreach (XmlNode childNode in xmlNodeList)
            {
                XmlElement childElement = (XmlElement)childNode;
                if (childElement.GetAttributeNode("id") == null)
                    continue;

                int id = Convert.ToInt32(childElement.GetAttributeNode("id").Value);
                if (id == 3)
                {
                    foreach (XmlNode cchildNode in childNode.ChildNodes)
                    {
                        XmlElement element = (XmlElement)cchildNode;
                        switch (element.Name)
                        {
                            case "callCount":
                                element.InnerText = "20";
                                break;
                            default:
                                break;
                        }
                    }
                }
                //移除节点
                if (id == 1002311)
                    root.RemoveChild(childNode);
            }

            xmlDocument.Save(path);

        }
        /// <summary>
        /// 添加XML节点
        /// </summary>
        public void AppendXMLChild(string path)
        {
            XmlDocument xmlDocument = new XmlDocument();
            xmlDocument.Load(path);
            XmlNode root = xmlDocument.SelectSingleNode("root");
            XmlNodeList xmlNodeList = xmlDocument.SelectSingleNode("root").ChildNodes;


            //创建一个新的节点
            XmlElement student = xmlDocument.CreateElement("student");
            student.SetAttribute("id", "112233");

            XmlElement name = xmlDocument.CreateElement("name");
            name.InnerText = "竹下";
            XmlElement callCount = xmlDocument.CreateElement("callCount");
            callCount.InnerText = "111";

            //设置父子关系
            student.AppendChild(name);
            student.AppendChild(callCount);

            //放入新节点
            root.AppendChild(student);

            xmlDocument.Save("./data.xml");
        }

        public DataTable ReadExcel(string path)
        {
            using (FileStream stream = File.Open(path, FileMode.Open, FileAccess.Read))
            {
                using (var reader = ExcelReaderFactory.CreateReader(stream))
                {
                    //Console.WriteLine("文件中表的数量："+reader.ResultsCount);
                    int formCount = reader.ResultsCount;
                    //for (int i = 0; i < formCount; i++)
                    {
                        Console.WriteLine("当前表格名称: " + reader.Name);
                        Console.WriteLine("当前表格列数: " + reader.FieldCount);
                        Console.WriteLine("当前表格行数: " + reader.RowCount);

                        ///读取日期（第一行）
                        List<string> date = new List<string>();
                        reader.Read();//Read()一次就是读取一行；
                        for (int i = 1; i < reader.FieldCount; i++)
                        {
                            date.Add(reader.GetValue(i).ToString());
                        }

                        ///读取具体数据
                        while (reader.Read())//按行读取,一个单元格占一位；
                        {
                            List<string> score = new List<string>();
                            for (int i = 0; i < reader.FieldCount; i++)
                            {
                                score.Add(reader.GetValue(i).ToString());
                                Console.Write(reader.GetValue(i) + "  ");
                            }
                            Console.WriteLine();
                        }
                    }

                }
            }

            return null;
        }
    }
}
