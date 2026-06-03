# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在此仓库中工作时提供指导。

## 项目概述

MathTechPy 是一个 PyQt6 桌面应用，用于数学教学管理——是对 C# Avalonia + ASP.NET Core 系统的 Python 重写。支持多班级学生数据管理、课堂随机抽人、基于 matplotlib 的多模式成绩分析图表、层级化知识点池维护，以及面向单个学生的知识点掌握度评估。

## 常用命令

```bash
# 激活虚拟环境（相对于项目根目录）
source ../.venv/bin/activate

# 运行应用
python main.py

# 杀掉残留进程后运行（按项目记忆，每次启动前执行）
pkill -f "python.*main.py" || true; python main.py

# 运行学生评估算法测试
python test_student_eval.py

# 生成/重新生成考试元数据（模拟教学进度的知识点分布）
python gen_exam_meta.py
```

项目未配置 lint/格式化工具或测试框架——唯一的测试是 `test_student_eval.py`，它端到端地验证核心评估算法。

## 架构

```
main.py                         # 入口：QApplication + matplotlib 配置 → MainWindow
├── core/
│   ├── models.py               # @dataclass：StudentData、ClassInfo、KnowledgeTopic、ExamMeta
│   ├── data_manager.py         # 单例。加载 XML（学生）+ XLSX（成绩），管理知识点池和考试元数据
│   └── random_engine.py        # 加权随机抽人，按 (班级, 模式) 隔离历史记录，避免重复
└── ui/
    ├── main_window.py          # 左侧导航栏（180px，5 个标签页）+ QStackedWidget 内容区
    ├── overview_tab.py         # 班级指标卡片 + 柱状图，带展开/收缩动画
    ├── random_combined_tab.py  # 五种随机抽人模式合一：弹跳、转盘、滚动轮盘、翻牌、分组
    ├── score_tab.py            # 五种图表模式：成绩分布直方图、个人趋势、最近一次、进退步榜、目标分对比
    ├── data_maintenance_tab.py # 知识点池 CRUD + 考试元数据编辑，拖拽排序分类，权重滑块
    └── student_eval_tab.py     # 单学生知识点掌握度：雷达图、知识点趋势、主客观对比
```

**数据流向**：XML（学生姓名、ID、点名次数）+ XLSX（考试成绩，每个评分模式一个 sheet：`40`/`100`）→ `DataManager` 单例 → 注入到每个 UI 标签页。标签页调用 `dm.current_students`、`dm.get_zscores()`、`dm.get_overview_data()` 等方法。`RandomEngine` 封装 DataManager 实现加权抽人，并在内存中维护自己的会话历史。

## 关键设计细节

- **多班级**：`config.xml` 中每个班级列出一对 `<classMembers>`（XML）和 `<classScore>`（XLSX）。班级从文件名中的数字自动检测，命名为 `A01`、`A03` 等。`DataManager.students[class_idx][mode]`，其中 mode 0 = 客观分（40分制），mode 1 = 满分卷（100分制）。
- **成绩模式**：应用中随处可见 `dm.use_full_score` 在"仅客观分"和"整卷分"之间切换。每个标签页都必须遵循此设置——侧边栏会显示当前的模式标签。
- **知识点池**：两级层级结构，持久化到 `data/knowledge_pool.xml`。默认值硬编码在 `DataManager.DEFAULT_POOL` 中（11 个一级分类，约 90 个二级知识点，覆盖高中数学内容）。可通过「数据维护」标签页编辑。
- **考试元数据**：`data/exam_meta.xml` 记录了每次考试日期中出现的知识点及其权重。`gen_exam_meta.py` 会按真实教学进度生成数据（例如先学函数，再学三角，最后学微积分），并随机加入滚动复习的知识点。
- **随机引擎**：加权抽人优先选择 `call_count` 较低的学生。历史记录以 `(class_idx, use_full_score)` 元组为键——切换班级会重置。候选人池耗尽时自动开启新一轮循环。
- **Z-score 归一化**：`dm.get_zscores()` 计算全班的每次考试 Z 分数。学生评估标签页进而按知识点出现频率加权，估算每个知识点的掌握程度。
- **标签页 refresh 合约**：每个标签页都暴露一个 `refresh()` 方法。`MainWindow.switch_tab()` 在新选中的标签页上调用它。`switch_class()` 也会在当前标签页上调用 `refresh()`。

## 依赖

```
PyQt6==6.11.0       # GUI 框架
matplotlib==3.10.9   # 图表（QtAgg 后端）
pandas==3.0.3        # 数据处理（轻度使用）
openpyxl==3.1.5      # Excel (.xlsx) 读取
```

## 注意事项

- 应用依赖 matplotlib 的中文字体支持。已配置的字体：Noto Serif CJK SC、WenQuanYi Micro Hei、AR PL UMing CN、SimHei。如果图表显示方块（□），请安装其中一款字体。
- 数据文件存放在 `data/` 目录下。`config.xml` 列出要加载的 XML+XLSX 文件对。`.bak` 文件是手动备份。
- `test_student_eval.py` 脚本以独立脚本形式验证学生评估算法——不使用测试框架，仅打印结果。
- **打包为 exe 时的数据目录问题**（待实施）：当前 `DataManager` 通过 `Path(__file__).parent.parent / "data"` 定位数据，PyInstaller 打包后 `__file__` 指向只读的 `sys._MEIPASS`。需改为：`sys.frozen` 时用 `Path(sys.executable).parent / "data"`，让 data 文件夹外置于 exe 同级目录。数据文件（XML 学生数据、knowledge_pool.xml、exam_meta.xml）需运行时写回，不能打入 exe 内部。
