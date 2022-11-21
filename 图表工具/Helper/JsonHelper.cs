using Newtonsoft.Json;
using System.Collections.Generic;
using System.IO;
using System;

namespace 图表工具.Helper
{
    public class JsonHelper
    {
        /// <summary>
        /// 将对象序列化为JSON格式
        /// </summary>
        /// <param name="o">对象</param>
        /// <returns>json字符串</returns>
        public static string SerializeObject(object o)
        {
            string json = JsonConvert.SerializeObject(o, Formatting.None);
            return json;
        }


        /// <summary>
        /// 读取文件
        /// </summary>
        /// <returns></returns>
        public static string ReadFile(string _folderName, string _jsonFileName)
        {
            string filePath = $"{AppDomain.CurrentDomain.BaseDirectory}data\\{_folderName}\\{_jsonFileName}.json";
            return File.Exists(filePath) ? File.ReadAllText(filePath) : "";
        }


        /// <summary>
        /// 保存文件
        /// </summary>
        public static void SaveFile(string _folderName, string _jsonFileName, string _jsonStr)
        {
            string _jsonPath = $"{AppDomain.CurrentDomain.BaseDirectory}data\\{_folderName}\\{_jsonFileName}.json";

            if (!Directory.Exists($"{AppDomain.CurrentDomain.BaseDirectory}data\\{_folderName}"))
            {
                Directory.CreateDirectory($"{AppDomain.CurrentDomain.BaseDirectory}data\\{_folderName}");
            }

            //json数据处理
            if (!string.IsNullOrEmpty(_jsonStr))
            {
                //写入文件
                File.WriteAllText(_jsonPath, _jsonStr);
            }
        }

        /// <summary>
        /// 删除文件
        /// </summary>
        /// <param name="_folderName"></param>
        /// <param name="_jsonFileName"></param>
        public static void DeleteFile(string _folderName, string _jsonFileName)
        {
            string _jsonPath = $"{AppDomain.CurrentDomain.BaseDirectory}data\\{_folderName}\\{_jsonFileName}.json";
            try
            {
                File.Delete(_jsonPath);
            }
            catch
            {
                //可能是路径不存在
            }
        }

        public static string ReadJsonFileText(object mapsPath)
        {
            throw new NotImplementedException();
        }

        /// <summary>
        /// 解析JSON字符串生成对象实体
        /// </summary>
        /// <typeparam name="T">对象类型</typeparam>
        /// <param name="json">json字符串(eg.{"ID":"112","Name":"石子儿"})</param>
        /// <returns>对象实体</returns>
        public static T DeserializeJsonToObject<T>(string json) where T : class
        {
            JsonSerializer serializer = new JsonSerializer();
            StringReader sr = new StringReader(json);
            object o = serializer.Deserialize(new JsonTextReader(sr), typeof(T));
            T t = o as T;
            return t;
        }

        /// <summary>
        /// 读取指定目录下的json文件
        /// </summary>
        /// <param name="path"></param>
        /// <returns></returns>
        public static string ReadJsonFileText(string path)
        {
            if (File.Exists(path))
                return File.ReadAllText(path);
            else return string.Empty;
        }

        /// <summary>
        /// 解析JSON数组生成对象实体集合
        /// </summary>
        /// <typeparam name="T">对象类型</typeparam>
        /// <param name="json">json数组字符串(eg.[{"ID":"112","Name":"石子儿"}])</param>
        /// <returns>对象实体集合</returns>
        public static List<T> DeserializeJsonToList<T>(string json) where T : class
        {
            JsonSerializer serializer = new JsonSerializer();
            StringReader sr = new StringReader(json);
            object o = serializer.Deserialize(new JsonTextReader(sr), typeof(List<T>));
            List<T> list = o as List<T>;
            return list;
        }

        /// <summary>
        /// 反序列化JSON到给定的匿名对象.
        /// </summary>
        /// <typeparam name="T">匿名对象类型</typeparam>
        /// <param name="json">json字符串</param>
        /// <param name="anonymousTypeObject">匿名对象</param>
        /// <returns>匿名对象</returns>
        public static T DeserializeAnonymousType<T>(string json, T anonymousTypeObject)
        {
            T t = JsonConvert.DeserializeAnonymousType(json, anonymousTypeObject);
            return t;
        }
    }
}
