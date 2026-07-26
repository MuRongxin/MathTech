# MathTech

Math 教学辅助工具仓库。**当前活跃开发仅 `MathTechPy/`**（Python PyQt6 桌面应用）。其余子项目为历史/实验性质，勿主动修改。

---

## 子项目状态

| 目录 | 技术栈 | 状态 |
|------|--------|------|
| `MathTechPy/` | Python 3 + PyQt6 + matplotlib | **活跃开发** |
| `Auxiliary tool/` | .NET Framework 4.7.2 WinForms | 原始版本，已冻结 |
| `AuxiliaryTool.Avalonia/` | .NET 8 Avalonia UI | 实验性重写，未完成 |
| `AuxiliaryTool.Web/` | .NET 10 ASP.NET Core API | 实验性重写，未完成 |

**规则：除非用户明确要求，只在 `MathTechPy/` 下工作。**

---

## MathTechPy 开发

### 环境与启动

```bash
# 虚拟环境在仓库根目录，非 MathTechPy 内
source .venv/bin/activate
cd MathTechPy

# 运行前先杀残留进程（matplotlib/Qt 在 Linux 上容易残留）
pkill -f "python.*main.py" || true
python main.py
```

### 测试

无测试框架。验证靠运行应用和手动测试。

### 无 lint/格式化/typecheck

项目未配置任何静态分析工具。

---

## MathTechPy 架构速查

```
main.py                    # 入口：QApplication + matplotlib 配置
core/
  models.py                # @dataclass: StudentData, ClassInfo, KnowledgeTopic, Question, ExamMeta
  data_manager.py          # 单例。加载 XML(学生)+CSV/XLSX(逐题分)，管理知识点池和考试元数据
  random_engine.py         # 加权随机抽人，历史按班级隔离、同班各模式共享
ui/
  main_window.py           # 左侧导航栏 + QStackedWidget
  widgets.py               # 共用组件（FlowLayout 等）
  overview_tab.py          # 班级指标卡片 + 柱状图
  random_combined_tab.py   # 五种随机抽人模式合一
  score_tab.py             # 五种图表模式
  data_maintenance_tab.py  # 知识点池 CRUD + 考试元数据编辑
  student_eval_tab.py      # 单学生知识点掌握度：雷达图、趋势
  data_admin_tab.py        # 学生管理 + 成绩文件导入
  init_dialog.py           # 首次启动初始化向导
```

**数据流**：`data/` 下 XML+CSV → `DataManager` 单例 → 注入各 UI 标签页。

### 关键设计

- **DataManager 单例**：用 `__new__` + `_initialized` 标志实现，不是普通 `__init__` 单例。导入 `DataManager()` 始终返回同一实例。
- **公开生命周期接口**：`reload()` 重载全部数据（名册+逐题分+校验）；`mark_initialized()` 标记初始化完成；`class_xml_path(ci)` 返回该班名册 XML 路径。加载错误存于 `dm._load_error`——仅 `config.xml` 缺失才触发初始化向导，其余加载错误（班级 XML 缺失、解析失败等）只记录不弹向导。
- **多班级**：`data/config.xml` 用多个 `classMembers` 节点列出每班名册 XML（不再有 `classScore` 配对）；逐题分从固定目录 `data/question_scores/` 扫描，按文件名 `quiz|exam_YYYY_MM_DD_班级` 的班级后缀匹配。班级名从名册文件名自动检测（正则 `r'[A-Za-z]*(\d+)'`），格式化为 `A01`、`A03` 等。
- **成绩三模式**：`StudentData` 有 `scores`（客观分）、`scores_sub`（主观分）、`scores_full`（全卷总分）三个独立列表。`_load_question_scores` 从 CSV/XLSX 逐题分自动计算并填充。
- **成绩存储格式**：`StudentData.scores`、`scores_sub`、`scores_full` 均为 `List[List[str]]`，每项为 `[date_str, score_str]`。score_str 以 `f"{float(val):.2f}"` 格式化（始终两位小数）。日期格式为 `"YYYY/MM/DD"`。
- **标签页刷新契约**：每个标签页暴露 `refresh()` 方法，`MainWindow.switch_tab()` 和 `switch_class()` 调用。
- **切班不重置抽人历史**：`switch_class()` 不再调用 `reset_history()`；`RandomEngine._history` 以班级索引为键，切换班级各自保留进度。
- **Z-score 归一化**：`dm.get_zscores()` 计算全班每次考试 Z 分（`(原始分 - μ) / σ`），返回 `[[name, [z1, z2, ...]], ...]`。缺考记为 `None`，不参与统计。
- **知识点池**：两级结构，持久化到 `data/knowledge_pool.xml`，默认值硬编码在 `DataManager.DEFAULT_POOL`（11 个一级分类，约 90 个二级知识点，覆盖高中数学）。**每次 CRUD 操作立即写回 XML**，非批量保存。
- **mtime 缓存**：`_load_question_scores` 把每个逐题分文件的解析结果按文件 mtime 缓存到 `.question_scores_cache.pkl`（tmp+`os.replace` 原子写回）；仅新增/修改过的文件重新解析，已删除文件的缓存条目自动丢弃。
- **题目结构检测**：`_detect_questions` 仅当 etype=exam、题号恰为 1-19 且各题 max_seen 与假设满分吻合时，套用固定结构 `_EXAM19_STRUCTURE`（Q1-8 单选/5、Q9-11 多选/6、Q12-14 填空/5、Q15-19 解答/13-17）；其余按观测推断（满分取 ceil(max_seen)，无人满分时会低估）并 WARN 提示人工核对。
- **callCount 批量写回**：`update_call_counts(class_idx, ids)` 内存更新后一次性写回该班 XML（`update_call_count` 为兼容包装）。所有 XML 写回（班级名册/knowledge_pool/exam_meta/逐题分缓存）均为 tmp+`os.replace` 原子写。
- **优雅初始化**：`config.xml` 缺失时 `_needs_init=True`，`main_window` 弹出 `InitDialog` 引导用户创建班级和学生。
- **数据定位**：`DataManager` 用 `Path(__file__).parent.parent / "data"` 定位数据。打包 exe 时需改为 `Path(sys.executable).parent / "data"`（尚未实施）。

### 易踩坑点

- **权重总和校验**：`data_maintenance_tab.py` 的 `_auto_save()`（防抖 500ms）在知识点权重总和 >100% 时拒绝保存，并调用 `_shake_all_tags()` 抖动标签变红提示。添加知识点时需注意总权重不超过 1.0。
- **FlowLayout 跨文件导入**：`FlowLayout` 已移到 `ui/widgets.py`，`random_tab.py` 保留 re-export（旧导入路径 `from ui.random_tab import FlowLayout` 仍可用）。修改 `widgets.py` 的 FlowLayout 会影响所有使用方。
- **OverviewTab 模式硬编码**：`overview_tab.py` 固定用 `self.dm.students[ci][1]`（满分卷），不响应模式切换。
- **exam_meta.xml 只写 questions**：保存时只写 `<questions>` 节点，旧格式的 `<subjective>`/`<objective>` 节点不再兼容。题型结构由 `_detect_questions` 检测（见"关键设计"），手写 exam_meta 时题型取值限 `choice`/`multi_select`/`fill`/`answer`。

### 依赖

```
PyQt6==6.11.0       # GUI
matplotlib==3.10.9  # 图表（QtAgg 后端，需中文字体支持）
openpyxl==3.1.5     # .xlsx 读取
```

中文字体：`Noto Serif CJK SC`, `WenQuanYi Micro Hei`, `AR PL UMing CN`, `SimHei`。图表显示方块时需安装其一。

---

## 其他子项目要点（仅在被要求时参考）

### Auxiliary tool (WinForms)

- .NET Framework 4.7.2，传统 `.csproj`，**不支持** `dotnet build`，需 MSBuild
- 文件名含空格和拼写错误（`RandomPanle`、`Score Analysis`），勿重命名——会脱钩 Designer 文件
- 运行时依赖 `config.xml` + 班级 XML + Excel 文件，缺失会崩溃
- 依赖 `user32.dll`，仅 Windows 可运行

### AuxiliaryTool.Web

- .NET 10 SDK 风格项目，`dotnet run` 可启动
- 数据文件在 `Data/` 子目录，`config.xml` 指定路径
- ExcelDataReader 在 Linux 需 `CodePagesEncodingProvider`

### AuxiliaryTool.Avalonia

- .NET 8 + Avalonia 11.2 + LiveChartsCore
- 未完成，仅有基础视图骨架

---

## 数据安全

Git 历史中可能残留真实学生姓名和成绩。当前分支已用模拟数据，但公开仓库前应清理历史。

---

## Git 分支

- `dev` — 当前活跃分支
- `master` — 稳定版
- `rebuild` — 重写尝试分支
