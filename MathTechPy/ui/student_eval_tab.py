"""学生评估页面 — 知识点掌握度分析"""
import math
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QLineEdit, QFrame, QPushButton, QButtonGroup, QCompleter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.data_manager import DataManager

# ExamMeta.subjective_topics → 客观题（40分制）
# ExamMeta.objective_topics  → 主观题（60分制）
TOPIC_OBJ = "subjective_topics"
TOPIC_SUB = "objective_topics"

VIEW_LABELS = [
    "客观题知识点分析",
    "主观题知识点分析",
    "主客观对比",
    "能力雷达图",
    "成绩历程",
    "知识点趋势",
]

SCORE_MODES = ["客观", "主观", "总体"]
MODE_COLORS = ["#3498db", "#e67e22", "#1abc9c"]


class StudentEvalTab(QWidget):
    """学生知识点掌握度评估"""

    def __init__(self, dm: DataManager):
        super().__init__()
        self.dm = dm
        self._current_student: str = ""
        self._view_mode = 3  # 默认雷达图
        self._score_mode = 0  # 0=客观, 1=主观, 2=总体
        self._filter_start: str = ""  # 日期筛选起始
        self._filter_end: str = ""    # 日期筛选截止
        self._setup_ui()

    # ------------------------------------------------------------------
    # UI 搭建
    # ------------------------------------------------------------------
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # ---- 工具栏 ----
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        toolbar.addWidget(QLabel("学生:"))
        self.combo_student = QComboBox()
        self.combo_student.setMinimumWidth(120)
        self.combo_student.setStyleSheet("""
            QComboBox {
                border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 4px 10px; font-size: 13px; background: white; color: #2c3e50;
            }
            QComboBox:hover { border-color: #1abc9c; }
            QComboBox QAbstractItemView {
                selection-background-color: #e0f0ea; selection-color: #2c3e50;
            }
        """)
        self.combo_student.currentIndexChanged.connect(self._on_student_changed)
        toolbar.addWidget(self.combo_student)

        # 对比按钮 + 对比学生下拉（雷达图专用）
        self.btn_compare = QPushButton("+对比")
        self.btn_compare.setCheckable(True)
        self.btn_compare.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_compare.setFixedHeight(30)
        self.btn_compare.setStyleSheet("""
            QPushButton {
                background: white; border: 2px solid #95a5a6; border-radius: 8px;
                padding: 4px 10px; font-size: 12px; color: #95a5a6;
            }
            QPushButton:checked { background: #1abc9c; color: white; border-color: #1abc9c; }
        """)
        self.btn_compare.clicked.connect(self._on_toggle_compare)
        self.btn_compare.setVisible(False)
        toolbar.addWidget(self.btn_compare)

        self.combo_compare = QComboBox()
        self.combo_compare.setMinimumWidth(120)
        self.combo_compare.setStyleSheet(self.combo_student.styleSheet())
        self.combo_compare.currentIndexChanged.connect(lambda: self.refresh())
        self.combo_compare.setVisible(False)
        toolbar.addWidget(self.combo_compare)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索学生...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 4px 10px; font-size: 13px; background: white; color: #2c3e50;
                min-width: 100px;
            }
            QLineEdit:focus { border-color: #1abc9c; }
        """)
        self.search_input.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_input)

        toolbar.addSpacing(8)

        toolbar.addWidget(QLabel("视图:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems(VIEW_LABELS)
        self.combo_mode.currentIndexChanged.connect(self._on_mode_changed)
        self.combo_mode.setMinimumWidth(150)
        self.combo_mode.setStyleSheet(self.combo_student.styleSheet())
        toolbar.addWidget(self.combo_mode)

        toolbar.addSpacing(8)

        # ---- 分数模式: 三段式分段按钮 ----
        self.score_btns: list[QPushButton] = []
        self.score_group = QButtonGroup(self)
        for i, (label, color) in enumerate(zip(SCORE_MODES, MODE_COLORS)):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(30)
            r_left = "8px" if i == 0 else "0px"
            r_right = "8px" if i == 2 else "0px"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white; border: 2px solid {color};
                    border-radius: {r_left} {r_right} {r_right} {r_left};
                    padding: 4px 14px; font-size: 12px; color: {color}; font-weight: bold;
                }}
                QPushButton:hover {{ background: #ecf0f1; }}
                QPushButton:checked {{ background: {color}; color: white; }}
            """)
            self.score_group.addButton(btn, i)
            toolbar.addWidget(btn)
            self.score_btns.append(btn)
        self.score_group.buttonClicked.connect(lambda btn: self.refresh())

        toolbar.addSpacing(12)

        # ---- 知识点下拉（趋势视图专用，默认隐藏）----
        self.combo_topic = QComboBox()
        self.combo_topic.setMinimumWidth(150)
        self.combo_topic.setStyleSheet(self.combo_student.styleSheet())
        self.combo_topic.currentIndexChanged.connect(lambda: self.refresh())
        self.combo_topic.setVisible(False)
        toolbar.addWidget(self.combo_topic)

        # ---- 趋势类型切换（趋势视图专用，默认隐藏）----
        self.trend_type_btns: list[QPushButton] = []
        self.trend_type_group = QButtonGroup(self)
        trend_colors = ["#3498db", "#e67e22", "#1abc9c"]
        for i, label in enumerate(["客观题", "主观题", "合并"]):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(30)
            r_left = "8px" if i == 0 else "0px"
            r_right = "8px" if i == 2 else "0px"
            color = trend_colors[i]
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white; border: 2px solid {color};
                    border-radius: {r_left} {r_right} {r_right} {r_left};
                    padding: 4px 12px; font-size: 12px; color: {color}; font-weight: bold;
                }}
                QPushButton:hover {{ background: #ecf0f1; }}
                QPushButton:checked {{ background: {color}; color: white; }}
            """)
            self.trend_type_group.addButton(btn, i)
            toolbar.addWidget(btn)
            self.trend_type_btns.append(btn)
            btn.setVisible(False)
        self.trend_type_group.buttonClicked.connect(lambda: self.refresh())

        # ---- 日期范围筛选 ----
        toolbar.addWidget(QLabel("起始:"))
        self.combo_start = QComboBox()
        self.combo_start.setMinimumWidth(100)
        self.combo_start.setStyleSheet(self.combo_student.styleSheet())
        self.combo_start.currentIndexChanged.connect(self._on_date_changed)
        toolbar.addWidget(self.combo_start)

        toolbar.addWidget(QLabel("截止:"))
        self.combo_end = QComboBox()
        self.combo_end.setMinimumWidth(100)
        self.combo_end.setStyleSheet(self.combo_student.styleSheet())
        self.combo_end.currentIndexChanged.connect(self._on_date_changed)
        toolbar.addWidget(self.combo_end)

        self.btn_recent7 = QPushButton("📅 近7次")
        self.btn_recent7.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recent7.setFixedHeight(30)
        self.btn_recent7.setStyleSheet("""
            QPushButton {
                background: #d5f5e3; border: none; border-radius: 8px;
                padding: 4px 14px; font-size: 12px; color: #1e8449;
            }
            QPushButton:hover { background: #a9dfbf; color: #145a32; }
        """)
        self.btn_recent7.clicked.connect(self._on_show_recent7)
        toolbar.addWidget(self.btn_recent7)

        self.btn_all = QPushButton("↺ 全部")
        self.btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_all.setFixedHeight(30)
        self.btn_all.setStyleSheet("""
            QPushButton {
                background: #ecf0f1; border: none; border-radius: 8px;
                padding: 4px 14px; font-size: 12px; color: #636e72;
            }
            QPushButton:hover { background: #dfe6e9; color: #2d3436; }
        """)
        self.btn_all.clicked.connect(self._on_show_all)
        toolbar.addWidget(self.btn_all)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ---- 统计摘要卡片 ----
        self.stats_frame = QFrame()
        self.stats_frame.setFixedHeight(68)
        self.stats_frame.setStyleSheet("""
            QFrame { background: white; border: 1px solid #ecf0f1; border-radius: 10px; }
        """)
        stats_layout = QHBoxLayout(self.stats_frame)
        stats_layout.setContentsMargins(20, 8, 20, 8)
        stats_layout.setSpacing(30)

        self.lbl_avg_obj = self._make_stat_label("客观分: --")
        self.lbl_avg_sub = self._make_stat_label("主观分: --")
        self.lbl_avg_full = self._make_stat_label("总分: --")
        self.lbl_call = self._make_stat_label("被抽: --")
        stats_layout.addWidget(self.lbl_avg_obj)
        stats_layout.addWidget(self.lbl_avg_sub)
        stats_layout.addWidget(self.lbl_avg_full)
        stats_layout.addWidget(self.lbl_call)
        stats_layout.addStretch()
        layout.addWidget(self.stats_frame)

        # ---- matplotlib 图表 ----
        self.fig = Figure(figsize=(10, 6.5), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("background: white; border: 1px solid #ecf0f1; border-radius: 10px;")
        layout.addWidget(self.canvas, 1)

        # ---- 状态栏 ----
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 2px 0; font-size: 12px;")
        layout.addWidget(self.status_label)

        # 初始化默认视图（在所有控件就绪后触发）
        self.combo_mode.setCurrentIndex(3)

    def _make_stat_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Microsoft YaHei", 11))
        lbl.setStyleSheet("color: #2c3e50; background: transparent;")
        return lbl

    # ------------------------------------------------------------------
    # 数据获取
    # ------------------------------------------------------------------
    def _get_student(self, name: str):
        for s in self.dm.current_students:
            if s.name == name:
                return s
        return None

    def _get_student_both(self, name: str):
        """同时从客观分和满分卷模式获取学生数据"""
        class_idx = self.dm.current_class
        obj_stu = None
        full_stu = None
        for s in self.dm.students[class_idx][0]:
            if s.name == name:
                obj_stu = s
                break
        for s in self.dm.students[class_idx][1]:
            if s.name == name:
                full_stu = s
                break
        return obj_stu, full_stu

    def _get_filtered_dates(self) -> set:
        """返回当前日期筛选范围内的日期集合"""
        if not self._filter_start and not self._filter_end:
            return set(self.dm.dates)  # 全部
        dates = self.dm.dates
        result = set()
        for d in dates:
            if self._filter_start and d < self._filter_start:
                continue
            if self._filter_end and d > self._filter_end:
                continue
            result.add(d)
        return result

    def _get_score_rates(self, student_name: str, score_type: str) -> dict:
        """获取学生各次考试的得分率 {date: rate}
        score_type: "obj"=客观分/40, "sub"=主观分/60, "full"=总分/100
        """
        obj_stu, full_stu = self._get_student_both(student_name)
        if obj_stu is None:
            return {}

        dates = self.dm.dates
        obj_scores = [float(s[1]) for s in obj_stu.scores] if obj_stu.scores else []
        full_scores = [float(s[1]) for s in full_stu.scores_full] if full_stu and full_stu.scores_full else []

        result = {}
        if score_type == "obj":
            for i, date in enumerate(dates):
                score = obj_scores[i] if i < len(obj_scores) else 0.0
                result[date] = round(score / 40.0, 4)
        elif score_type == "sub":
            for i, date in enumerate(dates):
                obj = obj_scores[i] if i < len(obj_scores) else 0.0
                ful = full_scores[i] if i < len(full_scores) else 0.0
                result[date] = round(max(0.0, ful - obj) / 60.0, 4)
        elif score_type == "full":
            for i, date in enumerate(dates):
                ful = full_scores[i] if i < len(full_scores) else 0.0
                result[date] = round(ful / 100.0, 4)
        return result

    def _build_topic_exam_map(self, topic_type: str, date_filter: set | None = None) -> dict:
        """建立 {topic_name: [(date, weight), ...]} 索引，支持日期过滤"""
        topic_map = {}
        for date, meta in self.dm.exam_meta.items():
            if date_filter and date not in date_filter:
                continue
            topics = getattr(meta, topic_type, [])
            for t in topics:
                if t.name not in topic_map:
                    topic_map[t.name] = []
                topic_map[t.name].append((date, t.weight))
        return topic_map

    def _compute_topic_performance(self, student_name: str, topic_type: str,
                                   score_rates: dict, date_filter: set | None = None) -> dict:
        """计算某学生在指定topic_type下各知识点的加权平均得分率"""
        topic_exam_map = self._build_topic_exam_map(topic_type, date_filter)
        if not topic_exam_map:
            return {}

        if not score_rates:
            return {}

        topic_category = {}
        for cat, topics in self.dm.knowledge_pool.items():
            for t in topics:
                topic_category[t] = cat

        result = {}
        for topic_name, exam_list in topic_exam_map.items():
            weighted_sum = 0.0
            total_weight = 0.0
            n_with_data = 0
            for date, weight in exam_list:
                if date in score_rates:
                    weighted_sum += score_rates[date] * weight
                    total_weight += weight
                    n_with_data += 1
            category = topic_category.get(topic_name, "未分类")
            if total_weight > 0:
                result[topic_name] = {
                    "rate": round(weighted_sum / total_weight, 3),
                    "count": n_with_data,
                    "category": category,
                }
            else:
                result[topic_name] = {"rate": None, "count": 0, "category": category}
        return result

    def _compute_category_performance(self, topic_scores: dict) -> dict:
        """按一级分类聚合知识点表现"""
        cats = {}
        for name, data in topic_scores.items():
            cat = data["category"]
            if data["rate"] is not None:
                if cat not in cats:
                    cats[cat] = {"rates": [], "topics": [], "count": 0}
                cats[cat]["rates"].append(data["rate"])
                cats[cat]["topics"].append(name)
                cats[cat]["count"] += 1
        for cat, d in cats.items():
            d["rate"] = round(sum(d["rates"]) / len(d["rates"]), 3) if d["rates"] else 0.0
        return cats

    def _compute_class_topic_performance(self, topic_type: str,
                                          date_filter: set | None = None) -> dict:
        """计算班级平均知识点表现 {topic: avg_rate}"""
        class_idx = self.dm.current_class
        students = [s.name for s in self.dm.students[class_idx][0]]
        if not students:
            return {}

        # 预先构建 topic_exam_map（所有学生共用，避免重复计算）
        topic_exam_map = self._build_topic_exam_map(topic_type, date_filter)
        if not topic_exam_map:
            return {}

        is_obj = (topic_type == TOPIC_OBJ)
        all_rates: dict[str, list[float]] = {}

        for name in students:
            if is_obj:
                rates = self._get_score_rates(name, "obj")
            else:
                rates = self._get_score_rates(name, "sub")
            # 直接用预构建的 exam_map 计算
            perf = self._compute_topic_performance_from_map(
                name, topic_exam_map, rates
            )
            for t, d in perf.items():
                if d["rate"] is not None:
                    if t not in all_rates:
                        all_rates[t] = []
                    all_rates[t].append(d["rate"])

        result = {}
        for t, rlist in all_rates.items():
            result[t] = round(sum(rlist) / len(rlist), 3)
        return result

    def _compute_topic_performance_from_map(self, student_name: str,
                                             topic_exam_map: dict,
                                             score_rates: dict) -> dict:
        """与 _compute_topic_performance 相同，但使用预构建的 topic_exam_map"""
        if not topic_exam_map or not score_rates:
            return {}

        topic_category = {}
        for cat, topics in self.dm.knowledge_pool.items():
            for t in topics:
                topic_category[t] = cat

        result = {}
        for topic_name, exam_list in topic_exam_map.items():
            weighted_sum = 0.0
            total_weight = 0.0
            n_with_data = 0
            for date, weight in exam_list:
                if date in score_rates:
                    weighted_sum += score_rates[date] * weight
                    total_weight += weight
                    n_with_data += 1
            category = topic_category.get(topic_name, "未分类")
            if total_weight > 0:
                result[topic_name] = {
                    "rate": round(weighted_sum / total_weight, 3),
                    "count": n_with_data,
                    "category": category,
                }
            else:
                result[topic_name] = {"rate": None, "count": 0, "category": category}
        return result

    # ------------------------------------------------------------------
    # 触发与刷新
    # ------------------------------------------------------------------
    def _on_student_changed(self, _idx):
        name = self.combo_student.currentText()
        if name:
            self._current_student = name
            self.refresh()

    def _on_mode_changed(self, idx):
        self._view_mode = idx
        if not hasattr(self, 'score_btns'):
            return  # UI 尚未就绪
        show_score = (idx in (3, 4))
        for btn in self.score_btns:
            btn.setVisible(show_score)
        self.combo_topic.setVisible(idx == 5)
        for btn in self.trend_type_btns:
            btn.setVisible(idx == 5)
        # 对比按钮仅雷达图（idx=3）显示
        show_compare = (idx == 3)
        self.btn_compare.setVisible(show_compare)
        if not show_compare:
            self.btn_compare.setChecked(False)
            self.combo_compare.setVisible(False)
        if self._current_student:
            self.refresh()

    def _on_toggle_compare(self):
        self.combo_compare.setVisible(self.btn_compare.isChecked())
        if self.btn_compare.isChecked():
            # 填充对比学生列表
            names = [self.combo_student.itemText(i)
                     for i in range(self.combo_student.count())]
            self.combo_compare.clear()
            self.combo_compare.addItems(names)
            # 默认选另一个
            cur = self.combo_student.currentText()
            for i, n in enumerate(names):
                if n != cur:
                    self.combo_compare.setCurrentIndex(i)
                    break
        self.refresh()

    def _on_search(self, text: str):
        for i in range(self.combo_student.count()):
            if text.lower() in self.combo_student.itemText(i).lower():
                self.combo_student.setCurrentIndex(i)
                return

    def _on_date_changed(self):
        self._filter_start = self.combo_start.currentText()
        self._filter_end = self.combo_end.currentText()
        if self._current_student:
            self.refresh()

    def _on_show_all(self):
        self.combo_start.blockSignals(True)
        self.combo_end.blockSignals(True)
        # 倒序：最早在末尾，最新在 index 0
        self.combo_start.setCurrentIndex(self.combo_start.count() - 1)
        self.combo_end.setCurrentIndex(0)
        self.combo_start.blockSignals(False)
        self.combo_end.blockSignals(False)
        self._filter_start = ""
        self._filter_end = ""
        if self._current_student:
            self.refresh()

    def _on_show_recent7(self):
        """筛选最近7次考试"""
        dates = self.dm.dates
        if not dates:
            return
        n = min(7, len(dates))
        self.combo_start.blockSignals(True)
        self.combo_end.blockSignals(True)
        # 倒序排列：index 0 = 最新(dates[-1]), index 6 = dates[-7]
        self.combo_end.setCurrentIndex(0)
        self.combo_start.setCurrentIndex(n - 1)
        self.combo_start.blockSignals(False)
        self.combo_end.blockSignals(False)
        self._filter_start = dates[-n]   # 原始顺序中倒数第 n 个
        self._filter_end = dates[-1]     # 最新
        if self._current_student:
            self.refresh()

    def refresh(self):
        self._score_mode = self.score_group.checkedId()
        if self._score_mode < 0:
            self._score_mode = 0

        # 初始化日期下拉框（首次或数据变更时）— 倒序排列
        dates = self.dm.dates
        if dates and (self.combo_start.count() == 0 or
                      self.combo_start.itemText(0) != dates[-1]):
            self.combo_start.blockSignals(True)
            self.combo_end.blockSignals(True)
            self.combo_start.clear()
            self.combo_end.clear()
            # 倒序：最新在前
            reversed_dates = list(reversed(dates))
            self.combo_start.addItems(reversed_dates)
            self.combo_end.addItems(reversed_dates)
            # 默认：截止=最后一次考试，起始=往前推 7 天
            last_date_str = dates[-1]
            self.combo_end.setCurrentIndex(0)  # 倒序后最新在 index 0
            try:
                last_dt = datetime.strptime(last_date_str, "%Y/%m/%d")
                week_ago = last_dt - timedelta(days=7)
                week_ago_str = week_ago.strftime("%Y/%m/%d")
                start_idx = 0
                for i, d in enumerate(dates):
                    if d >= week_ago_str:
                        start_idx = i
                        break
                # 倒序后 index = (N-1) - 原index
                rev_start_idx = len(dates) - 1 - start_idx
                self.combo_start.setCurrentIndex(rev_start_idx)
                self._filter_start = dates[start_idx]
            except ValueError:
                self.combo_start.setCurrentIndex(len(dates) - 1)
                self._filter_start = dates[0]
            self._filter_end = last_date_str
            self.combo_start.blockSignals(False)
            self.combo_end.blockSignals(False)

        self.combo_student.blockSignals(True)
        self.combo_student.clear()
        students = self.dm.current_students
        if not students:
            self._show_empty("当前班级没有学生数据")
            self.combo_student.blockSignals(False)
            return

        names = sorted([s.name for s in students])
        self.combo_student.addItems(names)

        completer = QCompleter(names)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_input.setCompleter(completer)

        if self._current_student and self._current_student in names:
            self.combo_student.setCurrentText(self._current_student)
        else:
            self._current_student = names[0]
            self.combo_student.setCurrentText(self._current_student)
        self.combo_student.blockSignals(False)

        obj_stu, full_stu = self._get_student_both(self._current_student)
        if obj_stu is None:
            self._show_empty("请从下拉列表选择学生")
            return

        stats = self._compute_stats(obj_stu, full_stu)
        self._update_stats(stats)

        has_obj = obj_stu and obj_stu.scores
        has_full = full_stu and full_stu.scores_full
        if not has_obj and not has_full:
            self._show_empty("该学生暂无成绩数据")
            return

        self.fig.clear()

        # 趋势视图：填充知识点下拉
        if self._view_mode == 5:
            date_filter = self._get_filtered_dates()
            obj_map = self._build_topic_exam_map(TOPIC_OBJ, date_filter)
            sub_map = self._build_topic_exam_map(TOPIC_SUB, date_filter)
            all_topics = sorted(set(obj_map.keys()) | set(sub_map.keys()))
            prev_topic = self.combo_topic.currentText()
            self.combo_topic.blockSignals(True)
            self.combo_topic.clear()
            self.combo_topic.addItems(all_topics)
            if prev_topic and prev_topic in all_topics:
                self.combo_topic.setCurrentText(prev_topic)
            self.combo_topic.blockSignals(False)

        try:
            if self._view_mode == 0:
                self._draw_topic_analysis(TOPIC_OBJ)
            elif self._view_mode == 1:
                self._draw_topic_analysis(TOPIC_SUB)
            elif self._view_mode == 2:
                self._draw_comparison()
            elif self._view_mode == 3:
                self._draw_radar()
            elif self._view_mode == 4:
                self._draw_timeline()
            elif self._view_mode == 5:
                self._draw_topic_trend()
        except Exception as e:
            self._show_error(str(e))
            return

        self.fig.tight_layout()
        self.canvas.draw()

    # ------------------------------------------------------------------
    # 统计摘要
    # ------------------------------------------------------------------
    def _compute_stats(self, obj_stu, full_stu) -> dict:
        obj_scores = [float(s[1]) for s in obj_stu.scores] if obj_stu and obj_stu.scores else []
        full_scores = [float(s[1]) for s in full_stu.scores_full] if full_stu and full_stu.scores_full else []
        n = min(len(obj_scores), len(full_scores))
        sub_scores = [max(0, full_scores[i] - obj_scores[i]) for i in range(n)]

        return {
            "avg_obj": round(sum(obj_scores) / len(obj_scores), 1) if obj_scores else None,
            "avg_sub": round(sum(sub_scores) / len(sub_scores), 1) if sub_scores else None,
            "avg_full": round(sum(full_scores) / len(full_scores), 1) if full_scores else None,
            "call_count": obj_stu.call_count if obj_stu else 0,
            "n_exams": n,
        }

    def _update_stats(self, stats: dict):
        def fmt(val, dash="--"):
            return f"{val:.1f}" if val is not None else dash

        self.lbl_avg_obj.setVisible(True)
        self.lbl_avg_sub.setVisible(True)
        self.lbl_avg_full.setVisible(True)

        if self._score_mode == 0:
            self.lbl_avg_obj.setText(f"客观均: <b style='color:#3498db'>{fmt(stats['avg_obj'])}</b>")
            self.lbl_avg_sub.setText(f"主观均: {fmt(stats['avg_sub'])}")
            self.lbl_avg_full.setText(f"总分均: {fmt(stats['avg_full'])}")
        elif self._score_mode == 1:
            self.lbl_avg_obj.setText(f"客观均: {fmt(stats['avg_obj'])}")
            self.lbl_avg_sub.setText(f"主观均: <b style='color:#e67e22'>{fmt(stats['avg_sub'])}</b>")
            self.lbl_avg_full.setText(f"总分均: {fmt(stats['avg_full'])}")
        else:
            self.lbl_avg_obj.setText(f"客观均: {fmt(stats['avg_obj'])}")
            self.lbl_avg_sub.setText(f"主观均: {fmt(stats['avg_sub'])}")
            self.lbl_avg_full.setText(f"总分均: <b style='color:#1abc9c'>{fmt(stats['avg_full'])}</b>")
        self.lbl_call.setText(f"被抽: <b style='color:#2c3e50'>{stats['call_count']}</b> 次")

    # ------------------------------------------------------------------
    # 绘图: 知识点分析（客观 / 主观）
    # ------------------------------------------------------------------
    def _draw_topic_analysis(self, topic_type: str):
        class_idx = self.dm.current_class
        date_filter = self._get_filtered_dates()
        is_obj = (topic_type == TOPIC_OBJ)

        if is_obj:
            score_rates = self._get_score_rates(self._current_student, "obj")
            label = "客观题"
            color_pos, color_neg = "#3498db", "#e74c3c"
        else:
            score_rates = self._get_score_rates(self._current_student, "sub")
            label = "主观题"
            color_pos, color_neg = "#e67e22", "#e74c3c"

        perf = self._compute_topic_performance(
            self._current_student, topic_type, score_rates, date_filter
        )
        if not perf:
            self._show_empty(f"暂无知识点数据，请先在数据维护页设置考试{label}的知识点。")
            return

        # 班级平均参照
        class_avg = self._compute_class_topic_performance(topic_type, date_filter)

        items = sorted(
            [(n, d) for n, d in perf.items() if d["rate"] is not None],
            key=lambda x: x[1]["rate"], reverse=True,
        )
        null_items = [(n, d) for n, d in perf.items() if d["rate"] is None]

        if not items:
            self._show_empty(f"该学生在{label}的知识点数据均为空。")
            return

        names = [x[0] for x in items] + [x[0] for x in null_items]
        rates = [x[1]["rate"] for x in items] + [0.0] * len(null_items)
        counts = [x[1]["count"] for x in items] + [0] * len(null_items)
        colors = [color_pos if r >= 0.5 else color_neg for r in rates]

        ax = self.fig.add_subplot(111)
        ax.set_xlim(-0.05, 1.05)

        n_topics = len(names)
        if n_topics > 30:
            y_pos = list(range(n_topics))
            ax.barh(y_pos, rates, color=colors, height=0.6)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names, fontsize=7)
            ax.invert_yaxis()
            ax.set_xlabel("加权得分率", fontsize=11)
            for i, (r, n) in enumerate(zip(rates, counts)):
                if n > 0:
                    ax.text(r + 0.01, i, f" {r:.0%}", va="center", fontsize=6)
            # 班级均线标记
            for i, name in enumerate(names):
                ca = class_avg.get(name)
                if ca is not None:
                    ax.plot(ca, i, "D", color="#7f8c8d", markersize=4, zorder=5)
        elif n_topics > 20:
            y_pos = list(range(n_topics))
            ax.barh(y_pos, rates, color=colors, height=0.6)
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names, fontsize=8)
            ax.invert_yaxis()
            ax.set_xlabel("加权得分率", fontsize=11)
            for i, (r, n) in enumerate(zip(rates, counts)):
                if n > 0:
                    ax.text(r + 0.01, i, f" {r:.0%} (n={n})", va="center", fontsize=7)
            for i, name in enumerate(names):
                ca = class_avg.get(name)
                if ca is not None:
                    ax.plot(ca, i, "D", color="#7f8c8d", markersize=5, zorder=5)
        else:
            x_pos = list(range(n_topics))
            ax.bar(x_pos, rates, color=colors, width=0.6)
            ax.set_xticks(x_pos)
            ax.set_xticklabels(names, fontsize=9, rotation=35, ha="right")
            ax.set_ylabel("加权得分率", fontsize=11)
            for i, (r, n) in enumerate(zip(rates, counts)):
                if n > 0:
                    ax.text(i, r + 0.02, f"{r:.0%}", ha="center", fontsize=8)
                    ax.text(i, 0.01, f"n={n}", ha="center", fontsize=7, color="#95a5a6")
            # 班级均线标记
            for i, name in enumerate(names):
                ca = class_avg.get(name)
                if ca is not None:
                    ax.plot(i, ca, "D", color="#7f8c8d", markersize=5, zorder=5)

        ax.axhline(y=0.5, color="#999", linewidth=0.8, linestyle="--", alpha=0.5)
        date_info = self._date_filter_info()
        ax.set_title(f"{self._current_student}  ·  {label}知识点分析(加权得分率){date_info}",
                     fontsize=14, fontweight="bold")
        weak = [f"{n}({r:.0%})" for n, r in items[-3:]] if len(items) >= 3 else []
        weak_str = f" | 薄弱: {', '.join(reversed(weak))}" if weak else ""
        if len(null_items) > 0:
            self.status_label.setText(
                f"{label}：{len(items)}个知识点有数据，{len(null_items)}个无数据{date_info}{weak_str}"
            )
        else:
            self.status_label.setText(f"{label}：共 {len(items)} 个知识点{date_info}{weak_str}")

    # ------------------------------------------------------------------
    # 绘图: 主客观对比
    # ------------------------------------------------------------------
    def _draw_comparison(self):
        class_idx = self.dm.current_class
        date_filter = self._get_filtered_dates()

        obj_rates = self._get_score_rates(self._current_student, "obj")
        sub_rates = self._get_score_rates(self._current_student, "sub")

        obj_perf = self._compute_topic_performance(
            self._current_student, TOPIC_OBJ, obj_rates, date_filter
        )
        sub_perf = self._compute_topic_performance(
            self._current_student, TOPIC_SUB, sub_rates, date_filter
        )

        common = []
        for name in set(obj_perf.keys()) & set(sub_perf.keys()):
            o_r = obj_perf[name]["rate"]
            s_r = sub_perf[name]["rate"]
            if o_r is not None or s_r is not None:
                o_r = o_r if o_r is not None else 0
                s_r = s_r if s_r is not None else 0
                common.append((name, o_r, s_r, abs(o_r - s_r)))

        if not common:
            self._show_empty("暂无主客观均设知识点的考试数据，无法对比。")
            return

        common.sort(key=lambda x: x[3], reverse=True)

        names = [x[0] for x in common]
        obj_d = [x[1] for x in common]
        sub_d = [x[2] for x in common]

        n_items = len(names)
        if n_items > 25:
            y_pos = list(range(n_items))
            w = 0.35
            ax = self.fig.add_subplot(111)
            ax.barh([y + w/2 for y in y_pos], obj_d, w, color="#3498db", label="客观题")
            ax.barh([y - w/2 for y in y_pos], sub_d, w, color="#e67e22", label="主观题")
            ax.set_yticks(y_pos)
            ax.set_yticklabels(names, fontsize=7)
            ax.invert_yaxis()
            ax.set_xlabel("加权得分率", fontsize=11)
            ax.set_xlim(-0.05, 1.05)
            ax.legend(fontsize=10, loc="lower right")
        else:
            ax = self.fig.add_subplot(111)
            x = list(range(n_items))
            w = 0.35
            bars1 = ax.bar([xi - w/2 for xi in x], obj_d, w, color="#3498db", label="客观题")
            bars2 = ax.bar([xi + w/2 for xi in x], sub_d, w, color="#e67e22", label="主观题")
            ax.set_xticks(x)
            ax.set_xticklabels(names, fontsize=9, rotation=35, ha="right")
            ax.set_ylabel("加权得分率", fontsize=11)
            ax.set_ylim(-0.05, 1.05)
            ax.legend(fontsize=11, loc="lower right")
            for bar in bars1:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.02,
                        f"{h:.0%}", ha="center", fontsize=7, color="#3498db")
            for bar in bars2:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, h + 0.02,
                        f"{h:.0%}", ha="center", fontsize=7, color="#e67e22")

        date_info = self._date_filter_info()
        ax.set_title(f"{self._current_student}  ·  主客观知识点对比{date_info}",
                     fontsize=14, fontweight="bold")
        self.status_label.setText(
            f"主客观对比：{len(common)} 个共有知识点，按差距降序排列{date_info}"
        )

    # ------------------------------------------------------------------
    # 绘图: 能力雷达图
    # ------------------------------------------------------------------
    def _draw_radar(self):
        class_idx = self.dm.current_class
        date_filter = self._get_filtered_dates()
        compare_name = self.combo_compare.currentText() if self.btn_compare.isChecked() else ""

        def _get_student_radar_vals(name: str) -> tuple[dict, dict]:
            """返回 (cat_obj, cat_sub) 或空"""
            o_r = self._get_score_rates(name, "obj")
            s_r = self._get_score_rates(name, "sub")
            op = self._compute_topic_performance(name, TOPIC_OBJ, o_r, date_filter)
            sp = self._compute_topic_performance(name, TOPIC_SUB, s_r, date_filter)
            return self._compute_category_performance(op), self._compute_category_performance(sp)

        cat_obj, cat_sub = _get_student_radar_vals(self._current_student)

        # 确定分类排序（以主学生为准）
        all_cats = sorted(
            set(cat_obj.keys()) | set(cat_sub.keys()),
            key=lambda c: (cat_obj.get(c, {}).get("rate", 0) +
                           cat_sub.get(c, {}).get("rate", 0)),
            reverse=True,
        )
        if len(all_cats) < 3:
            self._show_empty(f"类别数量不足3个（当前{len(all_cats)}），无法绘制雷达图。")
            return

        N = len(all_cats)
        angles = [n / N * 2 * math.pi for n in range(N)]
        angles += angles[:1]

        ax = self.fig.add_subplot(111, projection="polar")
        ax.set_theta_offset(math.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(all_cats, fontsize=10)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_yticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=8)

        if compare_name:
            # 多人对比模式：按分数模式取数据
            cat_cmp, cat_cmp_sub = _get_student_radar_vals(compare_name)

            def _pick_vals(co, cs):
                vals = []
                for c in all_cats:
                    o = co.get(c, {}).get("rate", 0)
                    s = cs.get(c, {}).get("rate", 0)
                    if self._score_mode == 0:
                        v = o
                    elif self._score_mode == 1:
                        v = s
                    else:
                        v = (o + s) / 2 if (o or s) else 0
                    vals.append(v)
                return vals + vals[:1]

            v1 = _pick_vals(cat_obj, cat_sub)
            v2 = _pick_vals(cat_cmp, cat_cmp_sub)
            ax.plot(angles, v1, "o-", color="#3498db", linewidth=2, markersize=6,
                    label=self._current_student)
            ax.fill(angles, v1, alpha=0.08, color="#3498db")
            ax.plot(angles, v2, "s--", color="#e67e22", linewidth=2, markersize=6,
                    label=compare_name)

            date_info = self._date_filter_info()
            ax.set_title(f"能力雷达图对比{date_info}", fontsize=14, fontweight="bold", pad=20)
            ax.legend(fontsize=11, loc="upper right", bbox_to_anchor=(1.3, 1.1))
            self.status_label.setText(
                f"对比: {self._current_student} vs {compare_name} | {N}个类别{date_info}"
            )
        else:
            # 单人模式：按分数模式显示
            obj_vals = [cat_obj.get(c, {}).get("rate", 0) for c in all_cats]
            sub_vals = [cat_sub.get(c, {}).get("rate", 0) for c in all_cats]
            obj_vals += obj_vals[:1]
            sub_vals += sub_vals[:1]

            if self._score_mode in (0, 2):  # 客观 or 总体
                ax.plot(angles, obj_vals, "o-", color="#3498db", linewidth=2, markersize=6,
                        label="客观题")
                ax.fill(angles, obj_vals, alpha=0.1, color="#3498db")
            if self._score_mode in (1, 2):  # 主观 or 总体
                ax.plot(angles, sub_vals, "s--", color="#e67e22", linewidth=2, markersize=6,
                        label="主观题")

            date_info = self._date_filter_info()
            ax.set_title(f"{self._current_student}  ·  能力雷达图{date_info}",
                         fontsize=14, fontweight="bold", pad=20)
            ax.legend(fontsize=11, loc="upper right", bbox_to_anchor=(1.3, 1.1))

            best_cat = max(all_cats, key=lambda c:
                cat_obj.get(c, {}).get("rate", 0) + cat_sub.get(c, {}).get("rate", 0))
            worst_cat = min(all_cats, key=lambda c:
                cat_obj.get(c, {}).get("rate", 0) + cat_sub.get(c, {}).get("rate", 0))
            best_rate = (cat_obj.get(best_cat, {}).get("rate", 0) +
                         cat_sub.get(best_cat, {}).get("rate", 0)) / 2
            worst_rate = (cat_obj.get(worst_cat, {}).get("rate", 0) +
                          cat_sub.get(worst_cat, {}).get("rate", 0)) / 2
            self.status_label.setText(
                f"雷达图：{N} 个类别 | 最强: {best_cat}({best_rate:.0%}) | "
                f"最弱: {worst_cat}({worst_rate:.0%}){date_info}"
            )

    # ------------------------------------------------------------------
    # 绘图: 成绩历程
    # ------------------------------------------------------------------
    def _draw_timeline(self):
        obj_stu, full_stu = self._get_student_both(self._current_student)
        if obj_stu is None or full_stu is None:
            self._show_empty("学生数据缺失")
            return

        obj_scores = [float(s[1]) for s in obj_stu.scores] if obj_stu.scores else []
        full_scores = [float(s[1]) for s in full_stu.scores_full] if full_stu.scores_full else []
        n = min(len(obj_scores), len(full_scores))
        if n == 0:
            self._show_empty("该学生暂无成绩数据")
            return

        dates = [s[0] for s in obj_stu.scores[:n]]
        obj_scores = obj_scores[:n]
        full_scores = full_scores[:n]
        sub_scores = [max(0.0, round(full_scores[i] - obj_scores[i], 1)) for i in range(n)]

        # 班级均线 — 从两个 mode 数组分别算
        class_idx = self.dm.current_class
        all_obj, all_full = [], []
        for s in self.dm.students[class_idx][0]:
            os_ = [float(v[1]) for v in s.scores] if s.scores else []
            if os_:
                all_obj.append(os_[:n])
        for s in self.dm.students[class_idx][1]:
            fs_ = [float(v[1]) for v in s.scores_full] if s.scores_full else []
            if fs_:
                all_full.append(fs_[:n])

        class_avg_obj, class_avg_sub, class_avg_full = [], [], []
        for i in range(n):
            col_obj = [a[i] for a in all_obj if i < len(a)]
            col_full = [a[i] for a in all_full if i < len(a)]
            avg_o = sum(col_obj) / len(col_obj) if col_obj else 0
            avg_f = sum(col_full) / len(col_full) if col_full else 0
            class_avg_obj.append(avg_o)
            class_avg_sub.append(max(0, avg_f - avg_o))
            class_avg_full.append(avg_f)

        x_ticks = list(range(n))
        x_labels = dates

        if self._score_mode == 0:
            # 客观模式：仅客观分
            ax = self.fig.add_subplot(111)
            ax.plot(x_ticks, obj_scores, "o-", color="#3498db", linewidth=2, markersize=5, label="客观分")
            ax.plot(x_ticks, class_avg_obj, "--", color="#3498db", linewidth=1, alpha=0.4, label="班均")
            ax.set_ylabel("客观分", fontsize=10, color="#3498db")
            ax.set_ylim(0, 42)
            ax.legend(fontsize=9, loc="upper left")
            ax.set_xticks(x_ticks)
            ax.set_xticklabels(x_labels, fontsize=8, rotation=35, ha="right")
            ax.set_title(f"{self._current_student}  ·  客观分历程", fontsize=14, fontweight="bold")
            self.status_label.setText(f"共 {n} 次考试 | 客观均{sum(obj_scores)/n:.1f}")

        elif self._score_mode == 1:
            # 主观模式：仅主观分
            ax = self.fig.add_subplot(111)
            ax.plot(x_ticks, sub_scores, "s-", color="#e67e22", linewidth=2, markersize=5, label="主观分")
            ax.plot(x_ticks, class_avg_sub, "--", color="#e67e22", linewidth=1, alpha=0.4, label="班均")
            ax.set_ylabel("主观分", fontsize=10, color="#e67e22")
            ax.set_ylim(0, 62)
            ax.legend(fontsize=9, loc="upper left")
            ax.set_xticks(x_ticks)
            ax.set_xticklabels(x_labels, fontsize=8, rotation=35, ha="right")
            ax.set_title(f"{self._current_student}  ·  主观分历程", fontsize=14, fontweight="bold")
            self.status_label.setText(f"共 {n} 次考试 | 主观均{sum(sub_scores)/n:.1f}")

        else:
            # 总体模式：三子图
            ax1 = self.fig.add_subplot(311)
            ax1.plot(x_ticks, obj_scores, "o-", color="#3498db", linewidth=2, markersize=5, label="客观分")
            ax1.plot(x_ticks, class_avg_obj, "--", color="#3498db", linewidth=1, alpha=0.4, label="班均")
            ax1.set_ylabel("客观分", fontsize=10, color="#3498db")
            ax1.set_ylim(0, 42)
            ax1.legend(fontsize=8, loc="upper left")
            ax1.set_xticks(x_ticks)
            ax1.set_xticklabels([])

            ax2 = self.fig.add_subplot(312)
            ax2.plot(x_ticks, sub_scores, "s-", color="#e67e22", linewidth=2, markersize=5, label="主观分")
            ax2.plot(x_ticks, class_avg_sub, "--", color="#e67e22", linewidth=1, alpha=0.4, label="班均")
            ax2.set_ylabel("主观分", fontsize=10, color="#e67e22")
            ax2.set_ylim(0, 62)
            ax2.legend(fontsize=8, loc="upper left")
            ax2.set_xticks(x_ticks)
            ax2.set_xticklabels([])

            ax3 = self.fig.add_subplot(313)
            ax3.plot(x_ticks, full_scores, "D-", color="#2ecc71", linewidth=2, markersize=5, label="总分")
            ax3.plot(x_ticks, class_avg_full, "--", color="#2ecc71", linewidth=1, alpha=0.4, label="班均")
            ax3.set_ylabel("总分", fontsize=10, color="#2ecc71")
            ax3.set_ylim(0, 105)
            ax3.legend(fontsize=8, loc="upper left")
            ax3.set_xticks(x_ticks)
            ax3.set_xticklabels(x_labels, fontsize=8, rotation=35, ha="right")

            ax1.set_title(f"{self._current_student}  ·  成绩历程", fontsize=14, fontweight="bold")
            self.status_label.setText(
                f"共 {n} 次考试 | 客观均{sum(obj_scores)/n:.1f} | "
                f"主观均{sum(sub_scores)/n:.1f} | 总分均{sum(full_scores)/n:.1f}"
            )

    # ------------------------------------------------------------------
    # 趋势数据: 基于逐题分的真实知识点得分率
    # ------------------------------------------------------------------
    def _build_question_topic_map(self, topic_name: str, date_filter: set) -> dict:
        """从 exam_meta.questions 建立 {date: [(qid, qtype, max_score, weight), ...]}"""
        result: dict[str, list[tuple]] = {}
        for date, meta in self.dm.exam_meta.items():
            if date_filter and date not in date_filter:
                continue
            if not meta.questions:
                continue
            for q in meta.questions:
                for kt in q.topics:
                    if kt.name == topic_name:
                        result.setdefault(date, []).append(
                            (q.id, q.qtype, q.max_score, kt.weight))
        return result

    def _compute_topic_trend_data(self, topic_name: str, date_filter: set,
                                   trend_type: int):
        """基于逐题分计算知识点趋势

        trend_type: 0=仅客观(choice), 1=仅主观(fill/answer), 2=合并
        返回: (data_points, class_avg_data)
        """
        import statistics

        # 从 question bindings 收集数据
        qt_map = self._build_question_topic_map(topic_name, date_filter)
        if not qt_map:
            return [], []

        student = self._current_student
        class_idx = self.dm.current_class
        all_names = [s.name for s in self.dm.students[class_idx][0]]

        # 按趋势类型过滤题目类型
        if trend_type == 0:
            allowed = {"choice", "multi_select"}
        elif trend_type == 1:
            allowed = {"fill", "answer"}
        else:
            allowed = None  # 合并模式不过滤

        student_points = []
        class_avg_points = []

        for date in sorted(qt_map.keys()):
            q_infos = qt_map[date]
            if allowed is not None:
                q_infos = [qi for qi in q_infos if qi[1] in allowed]
            if not q_infos:
                continue

            # 获取该学生和全班的逐题分
            stu_obj = None
            for s in self.dm.students[class_idx][0]:
                if s.name == student:
                    stu_obj = s
                    break
            if not stu_obj or date not in stu_obj.question_scores:
                continue
            stu_qs = stu_obj.question_scores[date]

            # 计算该学生在该知识点的得分率
            stu_score_sum = 0.0
            stu_max_sum = 0.0
            for qid, qtype, max_score, weight in q_infos:
                if qid in stu_qs:
                    stu_score_sum += stu_qs[qid]
                stu_max_sum += max_score

            if stu_max_sum == 0:
                continue
            s_val = round(stu_score_sum / stu_max_sum, 4)

            # 计算全班平均
            class_rates = []
            for name in all_names:
                name_qs = {}
                for s in self.dm.students[class_idx][0]:
                    if s.name == name:
                        name_qs = s.question_scores.get(date, {})
                        break
                if not name_qs:
                    continue
                ns_sum = 0.0
                nm_sum = 0.0
                for qid, qtype, max_score, weight in q_infos:
                    if qid in name_qs:
                        ns_sum += name_qs[qid]
                    nm_sum += max_score
                if nm_sum > 0:
                    class_rates.append(ns_sum / nm_sum)
            c_avg = round(statistics.mean(class_rates), 4) if class_rates else 0.0

            # 权重取所有相关题目的平均权重
            avg_weight = round(sum(qi[3] for qi in q_infos) / len(q_infos), 4)

            student_points.append((date, s_val, avg_weight, round(s_val * avg_weight, 4),
                                  q_infos[0][1]))
            class_avg_points.append((date, c_avg, avg_weight, q_infos[0][1]))

        return student_points, class_avg_points

    # ------------------------------------------------------------------
    # 绘图: 知识点趋势
    # ------------------------------------------------------------------
    def _draw_topic_trend(self):
        topic_name = self.combo_topic.currentText()
        if not topic_name:
            self._show_empty("请选择一个知识点")
            return

        trend_type = self.trend_type_group.checkedId()
        if trend_type < 0:
            trend_type = 0

        date_filter = self._get_filtered_dates()

        # 统计知识点在题目绑定中的出现次数
        qt_map = self._build_question_topic_map(topic_name, date_filter)
        total_n = len(qt_map)

        if total_n == 0:
            self._show_empty(f"知识点「{topic_name}」在当前日期范围内无考试数据（需先在数据维护页绑定知识点到题目）")
            return

        student_points, class_avg_points = self._compute_topic_trend_data(
            topic_name, date_filter, trend_type
        )

        if not student_points:
            self._show_empty(f"知识点「{topic_name}」在该题型筛选下无有效成绩数据")
            return

        # 计算登场类型描述
        if trend_type == 0:
            type_desc = "仅选择题"
        elif trend_type == 1:
            type_desc = "仅填空/解答题"
        else:
            type_desc = "全部题型"

        # 低置信度标记
        low_confidence = total_n < 3
        line_style = "--" if low_confidence else "-"
        confidence_note = "⚠️ 仅出现{}次，趋势仅供参考" if low_confidence else ""

        # 提取绘图数据
        dates_plot = [p[0] for p in student_points]
        s_vals = [p[1] for p in student_points]       # 原始值（得分率或 Z）
        weights = [p[2] for p in student_points]       # 权重（仅控制 marker 大小）
        e_types = [p[4] for p in student_points]      # 题型标记

        c_dates = [p[0] for p in class_avg_points]
        c_vals = [p[1] for p in class_avg_points]

        # marker 尺寸映射到权重 (12~48px²)
        if weights:
            min_w, max_w = min(weights), max(weights)
            if max_w > min_w:
                marker_sizes = [12 + (w - min_w) / (max_w - min_w) * 36 for w in weights]
            else:
                marker_sizes = [24] * len(weights)
        else:
            marker_sizes = [24] * len(weights)

        # 3 点滚动均线
        n_pts = len(s_vals)
        rolling = []
        for i in range(n_pts):
            start = max(0, i - 1)
            end = min(n_pts, i + 2)
            window = s_vals[start:end]
            rolling.append(sum(window) / len(window))

        # ---- 绘图 ----
        ax = self.fig.add_subplot(111)
        x = list(range(len(dates_plot)))

        # 班级均线（灰色虚线）
        ax.plot(x, c_vals, "s--", color="#bdc3c7", linewidth=1.2, markersize=5,
                label="班级均值", zorder=2)

        # 学生信号线（低置信度用虚线，颜色按趋势类型）
        trend_colors = ["#3498db", "#e67e22", "#1abc9c"]
        line_color = trend_colors[trend_type]
        student_label = f"{self._current_student}"

        ax.plot(x, s_vals, f"o{line_style}", color=line_color, linewidth=2,
                markersize=8, markerfacecolor="white", markeredgewidth=1.5,
                label=student_label, zorder=3)

        # 逐个画散点（大小映射权重）
        if trend_type == 2:
            # 合并模式：按题型分色标记
            obj_x = [x[i] for i in range(n_pts) if e_types[i] == "obj"]
            obj_y = [s_vals[i] for i in range(n_pts) if e_types[i] == "obj"]
            obj_s = [marker_sizes[i] for i in range(n_pts) if e_types[i] == "obj"]
            sub_x = [x[i] for i in range(n_pts) if e_types[i] == "sub"]
            sub_y = [s_vals[i] for i in range(n_pts) if e_types[i] == "sub"]
            sub_s = [marker_sizes[i] for i in range(n_pts) if e_types[i] == "sub"]
            if obj_x:
                ax.scatter(obj_x, obj_y, s=obj_s, c="#3498db", edgecolors="white",
                          linewidth=0.5, zorder=4, alpha=0.85)
            if sub_x:
                ax.scatter(sub_x, sub_y, s=sub_s, c="#e67e22", edgecolors="white",
                          linewidth=0.5, zorder=4, alpha=0.85)
        else:
            ax.scatter(x, s_vals, s=marker_sizes, c=line_color,
                      edgecolors="white", linewidth=0.5, zorder=4, alpha=0.85)

        # 滚动均线（橙色虚线）
        if n_pts >= 3:
            ax.plot(x, rolling, ":", color="#e74c3c", linewidth=1.8, alpha=0.7,
                    label="3点滚动均线", zorder=5)

        # 标注权重（每个点旁边）
        for i in range(n_pts):
            ax.annotate(f"w={weights[i]:.2f}",
                        (x[i], s_vals[i]),
                        textcoords="offset points", xytext=(0, 10),
                        fontsize=7, color="#7f8c8d", ha="center",
                        alpha=0.8)

        ax.set_xticks(x)
        ax.set_xticklabels(dates_plot, fontsize=8, rotation=35, ha="right")

        # Y 轴标签
        ax.set_ylabel("知识点得分率", fontsize=11)

        # Y 轴范围：得分率 0~1
        ax.set_ylim(-0.05, 1.05)
        ax.axhline(y=0.5, color="#999", linewidth=0.8, linestyle="--", alpha=0.5)

        ax.legend(fontsize=9, loc="upper left")
        ax.grid(axis="y", alpha=0.3)

        # 标题
        date_info = self._date_filter_info()
        conf_str = " ⚠️低置信度" if low_confidence else ""
        ax.set_title(
            f"{self._current_student}  ·  「{topic_name}」知识点趋势 ({type_desc}){conf_str}{date_info}",
            fontsize=14, fontweight="bold",
        )

        # 状态栏
        avg_val = sum(s_vals) / len(s_vals)
        parts = [
            f"「{topic_name}」{type_desc}",
            f"有效点{len(dates_plot)}个",
            f"均得分率={avg_val:.0%}",
        ]
        if low_confidence:
            parts.append(confidence_note.format(total_n))
        self.status_label.setText(" | ".join(parts))

    # ------------------------------------------------------------------
    # 辅助方法
    # ------------------------------------------------------------------
    def _date_filter_info(self) -> str:
        """返回日期筛选范围的描述文本"""
        if not self._filter_start and not self._filter_end:
            return ""
        if self._filter_start == self._filter_end:
            return f" [{self._filter_start}]"
        return f" [{self._filter_start} ~ {self._filter_end}]"

    def _show_empty(self, msg: str):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, msg, transform=ax.transAxes,
                ha="center", va="center", fontsize=16, color="#bdc3c7")
        ax.set_xticks([])
        ax.set_yticks([])
        self.fig.tight_layout()
        self.canvas.draw()
        self.status_label.setText(msg)

    def _show_error(self, msg: str):
        self._show_empty(f"出错了: {msg}")
