using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Auxiliary_tool
{
    public class StudentData
    {
        public int ID { get; set; }
        public string Name { get; set; }
        public int CallCount { get; set; }

        public List<float> Score  { get; set; }

        public List<Dictionary<string, string>> scoreList = new List<Dictionary<string, string>>();
        public Dictionary<string,List<string>> scoreDic=new Dictionary<string,List<string>>();
        public List<string[]> scoreArr = new List<string[]>();

        public StudentData(int id, string name, int callCount)
        {
            ID = id;
            Name = name;
            CallCount = callCount;
        }

        public string GetScoreInfoByDate(string date)
        {
            foreach (var item in scoreArr)
            {
                if (item[0] == date)
                    return item[1];
            }
            return null;
        }

    }
}
