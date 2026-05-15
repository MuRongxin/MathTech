# MathTech / Auxiliary tool — AI 代理项目指南

> 本文件面向 AI 编码代理。项目的主要自然语言为 **中文**（代码注释、UI 文本、文档均以中文为主）。

---

## 项目概览

**MathTech** 是一个用于高中数学教学场景的桌面辅助工具，当前仓库中仅保留核心子项目 `Auxiliary tool`。该工具为 Windows 窗体应用程序（WinForms），面向教师用户提供以下功能：

- **随机抽人（RandomPanle）**：从班级学生名单中随机抽取学生，并记录被抽中次数（`callCount`）。
- **成绩分析（Score Analysis）**：读取 Excel 成绩表，绘制学生成绩折线图，支持按学生筛选、分页浏览、仅查看最近 7 次成绩等。
- **数据看板（MainOverView / Form1）**：展示班级平均分趋势对比等总览信息。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 运行时 | .NET Framework 4.7.2 |
| UI 框架 | Windows Forms (Win32) |
| 项目格式 | 传统 .csproj (MSBuild 15.0) |
| IDE | Visual Studio 2022 (v17.1) |
| 图表库 | LiveCharts 0.9.7 + LiveCharts.WinForms + LiveCharts.Wpf |
| UI 控件库 | Guna.UI2.WinForms 2.0.3.5、HZH_Controls 1.0.14 |
| Excel 读取 | ExcelDataReader 3.7.0-develop00310 + ExcelDataReader.DataSet |
| 数据存储 | XML（学生名单）、Excel（成绩）、TXT（原始名单备份） |

---

## 项目结构

```
MathTech/
├── AGENTS.md                          # 本文件
└── Auxiliary tool/                    # 核心 C# WinForms 项目
    ├── Auxiliary tool.sln             # Visual Studio 解决方案
    ├── Auxiliary tool.csproj          # MSBuild 项目文件
    ├── packages.config                # NuGet 包引用（packages 文件夹已提交）
    ├── App.config                     # 应用配置（目标 .NET 4.7.2）
    ├── Program.cs                     # 程序入口，启动 Form1
    ├── Form1.cs / .Designer.cs / .resx    # 主窗体（无边框自定义标题栏 + 容器面板）
    ├── MainOverView.cs / .Designer.cs / .resx   # 总览面板 UserControl（当前占位）
    ├── Score Analysis.cs / .Designer.cs / .resx # 成绩分析面板 UserControl
    ├── RandomPanle.cs / .Designer.cs / .resx    # 随机抽人面板 UserControl
    ├── src/
    │   ├── Auxiliarymethods.cs        # 单例工具类：Excel/XML 读写、颜色/位置/尺寸动画、碰撞移动等
    │   ├── StudentData.cs             # 学生数据实体类
    │   └── ThemeColor.cs              # 随机主题色生成
    └── Properties/                    # 程序集信息、资源、设置
```

### 关键模块说明

- **`Form1`**：主窗体。包含 `overview_pane` 作为容器，通过按钮切换三个子面板（数据看板、随机抽人、成绩分析）。顶部有两个班级选择按钮（A01 / A02），必须先选择班级才能进入功能面板。
- **`RandomPanle`**：随机抽人界面。`randomTimer` 快速滚动学生姓名，`startRandomButton` 控制开始/停止；停止后更新被抽中学生的 `callCount` 并写入对应 XML。
- **`Score_Analysis_Panle`**：成绩分析界面。使用 `LiveCharts.WinForms.CartesianChart` 绘制折线图；支持下拉框直接选择学生、批量翻页、最近 7 天筛选、全部成绩/部分成绩切换。
- **`Auxiliarymethods`**（单例）：
  - 读写 `./config.xml` 获取四个数据文件路径（两个班级 XML、两个 Excel）。
  - 读写 `./data_A01.xml` / `./data_A02.xml` 存储学生名单与 `callCount`。
  - 读取 Excel 成绩表并将成绩绑定到 `StudentData.scoreArr`。
  - 提供一系列视觉动画辅助：平滑变色、平滑移动、碰撞边界移动、平滑改变尺寸。

---

## 构建与运行

### 环境要求

- Windows 操作系统（依赖 `user32.dll` 实现无边框窗体拖拽）
- Visual Studio 2019/2022 或 MSBuild（需安装 .NET Framework 4.7.2 目标包）
- 如使用 `dotnet` CLI：本项目为传统 .csproj，**不支持** `dotnet build`，请使用 MSBuild：

```powershell
# 在 "Auxiliary tool" 目录下
msbuild "Auxiliary tool.sln" /p:Configuration=Release
```

### 解决方案配置

| 配置 | 平台 | 输出目录 |
|------|------|----------|
| Debug | Any CPU | `bin\Debug\` |
| Release | Any CPU | `bin\Release\` |

### 运行时依赖文件

程序运行时需要与可执行文件同目录存在以下数据文件（由 `config.xml` 指定，默认为）：

- `config.xml` — 配置根文件，内含 4 个文件名
- `data_A01.xml` — A01 班学生名单（`id`, `name`, `callCount`）
- `data_A02.xml` — A02 班学生名单
- 两个 Excel 文件（如 `ExamA01Score.xlsx` / `ExamA02Score.xlsx`）— 成绩表

> 若缺失上述文件，程序在 `Form1_Load` 初始化阶段会抛出异常或崩溃。

---

## 代码风格与约定

- **命名风格**：采用 C# 传统 PascalCase / camelCase，但存在部分拼写不一致（如 `resoult` vs `result`、`Panle` vs `Panel`）。修改时应尽量保持与周围代码一致，避免大规模重命名导致设计器文件脱钩。
- **单例模式**：多个类使用手写懒加载单例（`if (_obj == null) _obj = new ...`），而非 `Lazy<T>`。
- **注释语言**：代码注释以中文为主，少量英文。
- **字符串硬编码**：文件路径、UI 文本大量硬编码，修改路径时需同步修改 `config.xml` 及 `Form1.cs` 中的相关逻辑。
- **UI 控件访问**：UserControl 之间通过 `Auxiliarymethods.Instance` 共享数据，也通过 `Form1.Instance` / `Score_Analysis_Panle.Instance` 直接访问控件。这是一种紧耦合设计，新增功能时应注意避免循环依赖。

---

## 测试说明

本项目 **没有单元测试项目**，也没有自动化测试框架。验证方式以手工运行（WinForms UI 测试）为主：

1. 确保 `config.xml` 及对应数据文件存在于可执行文件同级目录。
2. 启动程序后，先点击班级选择按钮（A01 或 A02）。
3. 测试随机抽人：切换到“随机抽人”面板，点击 Start / Stop，观察 `callCount` 是否正确写入 XML。
4. 测试成绩分析：切换到“成绩分析”面板，检查图表是否正确加载、下拉框筛选、翻页、最近 7 天切换是否正常。

---

## 安全与注意事项

- **数据安全**：项目历史提交中曾包含真实学生姓名与成绩。当前 `master` / `dev` 分支已替换为模拟数据，但 Git 历史记录中仍可能保留敏感信息。如需公开仓库，建议对历史进行清理（如 `git filter-repo` 或重新初始化仓库）。
- **代码签名**：项目中包含 `Auxiliary tool_TemporaryKey.pfx` 临时密钥文件，仅用于 ClickOnce 或本地测试签名，**不应视为生产密钥**。
- **依赖库版本**：`ExcelDataReader` 使用的是开发预览版 `3.7.0-develop00310`，升级前需验证 Excel 读取行为是否一致。
- **跨平台限制**：本项目深度依赖 Win32 API（`user32.dll`）及 WPF 互操作（`WindowsFormsIntegration`），无法直接在 Linux/macOS 上运行。

---

## 常见修改场景提示

| 场景 | 建议 |
|------|------|
| 新增班级 | 需修改 `config.xml` 结构、`Form1` 的班级按钮逻辑、`Auxiliarymethods` 中的数据列表与文件路径变量。 |
| 修改图表样式 | 在 `Score_Analysis_Panle` 或 `Form1` 中调整 `LiveCharts` 的 `SeriesCollection`、`Axis` 属性。 |
| 调整动画效果 | 修改 `Auxiliarymethods` 中的 `SmoothChangeColor`、`SmoothChangeLocation`、`SmoothMoveCollider` 等方法的步长参数。 |
| 替换数据源格式 | Excel 读取逻辑在 `Auxiliarymethods.ReadExcel`，XML 读写逻辑在 `ReadDataXml` / `CreatXMLFile` / `UpdataXmlData`。 |

---

> 最后更新：基于仓库当前 `dev` 分支状态生成。如发现项目结构或依赖发生显著变化，请同步更新本文件。
