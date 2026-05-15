using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml;
using ExcelDataReader;

namespace AuxiliaryTool.Avalonia.Models
{
    public class AuxiliaryMethods
    {
        public List<StudentData> studentDatas_1 = new List<StudentData>();
        public List<StudentData> studentDatas_2 = new List<StudentData>();
        public List<StudentData> studentDatas_1_2 = new List<StudentData>();
        public List<StudentData> studentDatas_2_2 = new List<StudentData>();
        public List<StudentData> studentDatas = new List<StudentData>();

        public int currentClass = 0;

        public string classFilePath_1 = "data_A01.xml";
        public string classFilePath_2 = "data_A02.xml";

        private static AuxiliaryMethods _obj;
        public static AuxiliaryMethods Instance
        {
            get
            {
                if (_obj == null)
                    _obj = new AuxiliaryMethods();
                return _obj;
            }
        }

        static Random random = new Random();

        public string GetRandomResult(List<string> data)
        {
            int temp = random.Next(data.Count);
            return data[temp];
        }

        public void ReadDataXml(string path, List<StudentData> studentData)
        {
            string callCount = "";
            string name = "";
            XmlDocument xmlDocument = new XmlDocument();
            xmlDocument.Load(path);

            XmlNodeList xmlNodeList = xmlDocument.SelectSingleNode("root").ChildNodes;
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

        public string[] ReadConfig(string path)
        {
            string[] filePath = new string[4];

            XmlDocument xmlDocument = new XmlDocument();
            xmlDocument.Load(path);

            XmlNodeList xmlNodeList = xmlDocument.SelectSingleNode("config").ChildNodes;

            for (int i = 0; i < xmlNodeList.Count; i++)
                filePath[i] = xmlNodeList[i].InnerText;

            return filePath;
        }

        public void CreateXmlFile(string path, string[] dataArray)
        {
            XmlDocument xmlDocument = new XmlDocument();
            XmlDeclaration xmlDeclaration = xmlDocument.CreateXmlDeclaration("1.0", "UTF-8", "");
            xmlDocument.AppendChild(xmlDeclaration);

            List<string> oriData = dataArray.ToList<string>();
            XmlElement root = xmlDocument.CreateElement("root");

            foreach (var item in oriData)
            {
                string[] strtemp = item.Split(' ');
                XmlElement student = xmlDocument.CreateElement("student");
                student.SetAttribute("id", strtemp[0]);

                XmlElement name = xmlDocument.CreateElement("name");
                name.InnerText = strtemp[1];

                XmlElement callCount = xmlDocument.CreateElement("callCount");
                callCount.InnerText = "0";

                root.AppendChild(student);
                student.AppendChild(name);
                student.AppendChild(callCount);
            }

            xmlDocument.AppendChild(root);
            xmlDocument.Save(path);
        }

        public void UpdateXmlData(string path, int stuId, int value)
        {
            XmlDocument xmlDocument = new XmlDocument();
            xmlDocument.Load(path);
            XmlNode root = xmlDocument.SelectSingleNode("root");
            XmlNodeList xmlNodeList = xmlDocument.SelectSingleNode("root").ChildNodes;

            foreach (XmlNode childNode in xmlNodeList)
            {
                XmlElement childElement = (XmlElement)childNode;
                if (childElement.GetAttributeNode("id") == null)
                    continue;

                int id = Convert.ToInt32(childElement.GetAttributeNode("id").Value);
                if (id == stuId)
                {
                    foreach (XmlNode cchildNode in childNode.ChildNodes)
                    {
                        XmlElement element = (XmlElement)cchildNode;
                        if (element.Name == "callCount")
                        {
                            element.InnerText = value.ToString();
                            break;
                        }
                    }
                }
            }

            xmlDocument.Save(path);
        }

        public void AppendXmlChild(string path)
        {
            XmlDocument xmlDocument = new XmlDocument();
            xmlDocument.Load(path);
            XmlNode root = xmlDocument.SelectSingleNode("root");

            XmlElement student = xmlDocument.CreateElement("student");
            student.SetAttribute("id", "999999");

            XmlElement name = xmlDocument.CreateElement("name");
            name.InnerText = "测试";
            XmlElement callCount = xmlDocument.CreateElement("callCount");
            callCount.InnerText = "111";

            student.AppendChild(name);
            student.AppendChild(callCount);
            root.AppendChild(student);

            xmlDocument.Save(path);
        }

        public void ReadExcel(string path, List<StudentData> studentDatas, int tableIndex = 0)
        {
            using (FileStream stream = File.Open(path, FileMode.Open, FileAccess.Read))
            {
                using (var reader = ExcelReaderFactory.CreateReader(stream))
                {
                    for (int i = 0; i < tableIndex; i++)
                    {
                        reader.NextResult();
                    }

                    List<string> date = new List<string>();
                    reader.Read();
                    for (int i = 1; i < reader.FieldCount; i++)
                    {
                        if (reader.GetValue(i) == null)
                            continue;
                        date.Add(reader.GetValue(i).ToString());
                    }

                    while (reader.Read())
                    {
                        List<string> score = new List<string>();
                        for (int i = 0; i < reader.FieldCount; i++)
                        {
                            if (reader.GetValue(i) == null)
                                continue;
                            if (i > 0)
                                score.Add(float.Parse(reader.GetValue(i).ToString()).ToString("#0.00"));
                            else
                                score.Add(reader.GetValue(i).ToString());
                        }

                        foreach (var item in studentDatas)
                        {
                            if (score.Count == 0)
                                continue;
                            if (item.Name.Replace(" ", "") == score[0])
                            {
                                for (int z = 0; z < date.Count; z++)
                                {
                                    item.scoreList.Add(new Dictionary<string, string>() { { date[z], score[z + 1] } });
                                    item.scoreArr.Add(new string[2] { date[z], score[z + 1] });
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
