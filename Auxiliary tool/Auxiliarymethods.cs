using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Auxiliary_tool
{
    class Auxiliarymethods
    {
       
        public List<string> dataList_1 = new List<string>();
        public List<string> dataList_2 = new List<string>();

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
    }
}
