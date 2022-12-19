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

        public List<StudentData> studentDatas_1 = new List<StudentData>();
        public List<StudentData> studentDatas_2 = new List<StudentData>();

        public List<StudentData> studentDatas = new List<StudentData>();

        

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

        public void ReadTxtData()
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
        public void ChangepanelColor(Panel panel, Color falColor, out Color resColor)
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

        Dictionary<string, Color> resoultColorsDic = new Dictionary<string, Color>();//存储每个控件的目标颜色；

        /// <summary>
        /// 平滑改变控件颜色
        /// </summary>
        /// <param name="oriColor">控件现在的颜色</param>
        /// <param name="key">控件名</param>
        /// <returns></returns>
        public Color SmoothChangeColor(Color oriColor, string key)
        {
            Color falColor ;

            if (!resoultColorsDic.ContainsKey(key))//如果当前没有该控件的颜色信息；
                resoultColorsDic.Add(key, ThemeColor.RandomColor());

            if (oriColor == resoultColorsDic[key])
                resoultColorsDic[key] = ThemeColor.RandomColor();

            falColor = SmoothChangeColor(oriColor, resoultColorsDic[key]);
            
            return falColor;
        }

        public Color SmoothChangeColor(Color oriColor, Color targetColor)
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

            return tempColor;

        }

        /// <summary>
        /// 平滑过度数字
        /// </summary>
        /// <param name="startValue">起始数值</param>
        /// <param name="targetValue">目标数值</param>
        /// <returns></returns>
        public int SmoothChangeValue(int startValue,int targetValue,int range,bool isIncrease = true)
        {
            if (isIncrease)
            {
                if (startValue <= targetValue)
                    targetValue = startValue + range;
            }
            else
                if (startValue >= targetValue)
                targetValue = startValue - range;

            return targetValue;
        }

        public Dictionary<string,Point> targetLocationDic=new Dictionary<string,Point>();
        public Point SmoothChangeLocation(Point oriLocation,string key,int randomRange,int changeRange)
        {
            if (!targetLocationDic.ContainsKey(key))
                targetLocationDic.Add(key, GetRandomLocation(oriLocation, randomRange));

            if (JudgeControlSpacing(oriLocation, targetLocationDic[key]) < 2.5)
                targetLocationDic[key] = GetRandomLocation(oriLocation, randomRange);

            return SmoothChangeLocation(oriLocation, targetLocationDic[key], changeRange);
        }

        private Point SmoothChangeLocation(Point oriLocation, Point targetLocation,int range)
        {
            if (oriLocation.X < targetLocation.X)
                oriLocation.X += range;
            if (oriLocation.X > targetLocation.X)
                oriLocation.X -= range;

            if (oriLocation.Y < targetLocation.Y)
                oriLocation.Y += range;
            if (oriLocation.Y > targetLocation.Y)
                oriLocation.Y -= range;

            return oriLocation;
        }

        private Point GetRandomLocation(Point oriLocation,int range)
        {
            Random random = new Random();

            if (random.Next(-1, 2) < 0)
                range = -range;

            int startX = 0, endX = 0;
            int startY = 0, endY = 0;

            if (oriLocation.X < oriLocation.X + range) { 
                startX = oriLocation.X; endX = oriLocation.X + range;}
            else
                endX = oriLocation.X; startX = oriLocation.X + range;

            if (oriLocation.Y < oriLocation.Y + range) { 
                startY = oriLocation.Y; endY = oriLocation.Y + range;}
            else
                endY = oriLocation.Y; startY = oriLocation.Y + range;

            int x = random.Next(startX, endX);
            int y = random.Next(startY, endY);

            return new Point(x, y);
        }

        private double JudgeControlSpacing(Point currentLocation,Point targetLocation)
        {
            int x = Math.Abs(currentLocation.X - targetLocation.X);
            int y = Math.Abs(currentLocation.Y - targetLocation.Y);

            return Math.Sqrt(Math.Pow(x, 2) + Math.Pow(y, 2));
        }

        /// <summary>
        /// ReadDataXml
        /// </summary>
        /// <param name="path"></param>
        public void ReadDataXml(string path, List<StudentData> studentData)
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
                studentData.Add(new StudentData(id, name, int.Parse(callCount)));               
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

            xmlDocument.Save(path);
        }
        /// <summary>
        /// Excel 读取，务必在xml读取之后调用；
        /// </summary>
        /// <param name="path"></param>
        public void ReadExcel(string path,List<StudentData> studentDatas)
        {
            using (FileStream stream = File.Open(path, FileMode.Open, FileAccess.Read))
            {
                using (var reader = ExcelReaderFactory.CreateReader(stream))
                {
                    reader.NextResult();//只读取第二个表的数据
                    int formCount = reader.ResultsCount;//文件中表的数量
                    //for (int i = 0; i < formCount; i++)//如果要读取所有的表，则启动循环；
                    {
                        string formName = reader.Name;//当前表格名称;
                        int colCount = reader.FieldCount;//当前表格列数;     
                        int rowCount = reader.RowCount;//当前表格行数;

                        ///读取日期（第一行）
                        List<string> date = new List<string>();
                        reader.Read();//Read()一次就是读取一行；
                        for (int i = 1; i < reader.FieldCount; i++)
                        {
                            date.Add(reader.GetValue(i).ToString());
                        }

                        /// 通过 AsDataSet 操作数据;
                        //var res = reader.AsDataSet();
                        //string temp = res.Tables[1].Rows[1][0].ToString();

                        ///读取具体数据
                        while (reader.Read())//按行读取,一个单元格占一位；
                        {
                            List<string> score = new List<string>();
                            for (int i = 0; i < reader.FieldCount; i++)
                            {
                                if (i > 0)//去除多余的小数位数；
                                    score.Add(float.Parse(reader.GetValue(i).ToString()).ToString("#0.00"));
                                else
                                    score.Add(reader.GetValue(i).ToString());
                            }


                            ///读取完一行就处理一行的数据；
                            foreach (var item in studentDatas)
                            {
                                if (item.Name.Replace(" ", "") == score[0])
                                {
                                    for (int z = 0; z < date.Count; z++)//因为去除了第一位的缘故，date（日期）比score少一位；
                                    {                                      

                                        item.scoreDic.Add(new Dictionary<string, string>() { { date[z], score[z + 1] } });
                                        item.scoreArr.Add(new string[2] { date[z], score[z + 1] });
                                    }

                                }
                            }
                        }
                        ///读取下一张表;(如果需要的话)
                        reader.NextResult();
                    }
                }

            }        
           
        }
        /// <summary>
        /// 获取组件的所有子控件，包括子控件的子控件，从childControlList获取数结果；
        /// </summary>
        /// <param name="panel"></param>

        public List<Control> GetControlChildControl(Control control)
        {
            List<Control> childControlList = new List<Control>();
            GetChildControl(control, childControlList);

            return childControlList;
        }
        private void GetChildControl(Control control, List<Control> childControlList)
        {
            if (control.Controls.Count == 0)
                return;

            for (int i = 0; i < control.Controls.Count; i++)
            {
                childControlList.Add(control.Controls[i]);
                GetChildControl(control.Controls[i], childControlList);
            }
        }
    }
}
