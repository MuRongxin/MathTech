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

        public StudentData(int id,string name,int callCount)
        {
            ID = id;
            Name = name;
            CallCount = callCount;
        }

    }
}
