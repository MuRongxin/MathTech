using System.Text;
using AuxiliaryTool.Web.Models;

// ExcelDataReader needs code pages encoding provider on Linux
Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

var builder = WebApplication.CreateBuilder(args);

// Add controllers
builder.Services.AddControllers();

var app = builder.Build();

// Set data base path and load data
var dataPath = Path.Combine(app.Environment.ContentRootPath, "Data");
AuxiliaryMethods.Instance.BasePath = dataPath;

var configPath = Path.Combine(dataPath, "config.xml");
if (File.Exists(configPath))
{
    var paths = AuxiliaryMethods.Instance.ReadConfig(configPath);
    var xml1 = Path.Combine(dataPath, paths[0]);
    var xml2 = Path.Combine(dataPath, paths[1]);
    var excel1 = Path.Combine(dataPath, paths[2]);
    var excel2 = Path.Combine(dataPath, paths[3]);

    // Load class 1
    AuxiliaryMethods.Instance.studentDatas_1.Clear();
    AuxiliaryMethods.Instance.studentDatas_1_2.Clear();
    AuxiliaryMethods.Instance.ReadDataXml(xml1, AuxiliaryMethods.Instance.studentDatas_1);
    AuxiliaryMethods.Instance.ReadDataXml(xml1, AuxiliaryMethods.Instance.studentDatas_1_2);
    AuxiliaryMethods.Instance.ReadExcel(excel1, AuxiliaryMethods.Instance.studentDatas_1);
    AuxiliaryMethods.Instance.ReadExcel(excel1, AuxiliaryMethods.Instance.studentDatas_1_2, 1);

    // Load class 2
    AuxiliaryMethods.Instance.studentDatas_2.Clear();
    AuxiliaryMethods.Instance.studentDatas_2_2.Clear();
    AuxiliaryMethods.Instance.ReadDataXml(xml2, AuxiliaryMethods.Instance.studentDatas_2);
    AuxiliaryMethods.Instance.ReadDataXml(xml2, AuxiliaryMethods.Instance.studentDatas_2_2);
    AuxiliaryMethods.Instance.ReadExcel(excel2, AuxiliaryMethods.Instance.studentDatas_2);
    AuxiliaryMethods.Instance.ReadExcel(excel2, AuxiliaryMethods.Instance.studentDatas_2_2, 1);

    AuxiliaryMethods.Instance.classFilePath_1 = xml1;
    AuxiliaryMethods.Instance.classFilePath_2 = xml2;
    AuxiliaryMethods.Instance.currentClass = 1;
    AuxiliaryMethods.Instance.studentDatas = AuxiliaryMethods.Instance.studentDatas_1;
}

app.UseDefaultFiles();
app.UseStaticFiles();
app.MapControllers();

app.Run();
