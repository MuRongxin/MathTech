using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using 图表工具.Helper;
using 图表工具.Models;

namespace 图表工具.LocalData
{
    public class ReportData
    {
        static string dataPath = $"{Application.StartupPath}\\data\\reportData.json";

        public static List<ResportDataModel> ResportDatas;
        public static List<ColumnModel> Columns = new List<ColumnModel>();

        static ReportData()
        {
            Read();
        }

        public static void Read()
        {
            string jsonStr = JsonHelper.ReadJsonFileText(dataPath);
            ResportDatas = JsonHelper.DeserializeJsonToList<ResportDataModel>(jsonStr);

            if (ResportDatas != null && ResportDatas.Count > 0)
            {
                Columns.Clear();
                for (int i = 0; i < ResportDatas[0].Columns.Count; i++)
                {
                    Columns.Add(new ColumnModel()
                    {
                        ColumnName = ResportDatas[0].Columns[i].ColumnName,
                        ColumnValue = 0
                    });
                }
            }
            else
            {
                Columns = new List<ColumnModel>();
                ResportDatas = new List<ResportDataModel>();
                Save();
            }
        }

        public static void Add(ResportDataModel _model)
        {
            ResportDatas.Add(_model);
            Save();
        }

        public static void AddColumn(string _name)
        {
            Columns.Add(new ColumnModel() { ColumnName = _name, ColumnValue = 0 });
            for (int i = 0; i < ResportDatas.Count; i++)
            {
                ResportDatas[i].Columns.Add(new ColumnModel()
                {
                    ColumnName = _name,
                    ColumnValue = 0
                });
            }
            Save();
        }

        public static void RemoveColumn(string _name)
        {
            Columns.RemoveAll(c => c.ColumnName == _name);
            for (int i = 0; i < ResportDatas.Count; i++)
            {
                ResportDatas[i].Columns.RemoveAll(c => c.ColumnName == _name);
            }
            Save();
        }

        public static void UpdateColumn(string _oldName, string _newName)
        {
            Columns.Single(c => c.ColumnName == _oldName).ColumnName = _newName;
            for (int i = 0; i < ResportDatas.Count; i++)
            {
                ResportDatas[i].Columns.Single(c => c.ColumnName == _oldName).ColumnName = _newName;
            }
            Save();
        }

        public static void UpdateDate(string _id, DateTime _date)
        {
            ResportDatas.Single(c => c.Id == _id).ReportDate = _date;
            Save();
        }

        public static void UpdateColumnValue(string _id, string _columnName, double _columnValue)
        {
            ResportDatas.Single(c => c.Id == _id).Columns.Single(c => c.ColumnName == _columnName).ColumnValue = _columnValue;
            Save();
        }

        public static void Clear()
        {
            ResportDatas.Clear();
            Save();
        }

        public static void Save()
        {
            string _content = JsonHelper.SerializeObject(ResportDatas);

            if (!File.Exists(dataPath))
            {
                var s = File.Create(dataPath);
                s.Close();
                s.Dispose();
            }

            //json数据处理
            if (!string.IsNullOrEmpty(_content))
            {
                //写入文件
                File.WriteAllText(dataPath, _content);
            }
        }

        public static void RemoveData(string _id)
        {
            ResportDatas.RemoveAll(c=>c.Id==_id);
            Save();
        }
    }
}
