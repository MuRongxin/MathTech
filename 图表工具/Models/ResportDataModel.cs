

using System;
using System.Collections.Generic;

namespace 图表工具.Models
{
    public class ResportDataModel
    {
        public string Id { get; set; }
        public DateTime ReportDate { get; set; }
        public List<ColumnModel> Columns { get; set; }
    }

    public class ColumnModel 
    {
        public string ColumnName { get; set; }
        public double ColumnValue { get; set; }
    }
}
