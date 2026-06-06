"""QPainter 雷达图 — 实验性页面，与 StudentEvalTab 雷达图功能一致"""
import math
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QButtonGroup, QLineEdit, QCompleter,
)
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QPainterPath, QPen, QBrush, QPolygonF,
)

from core.data_manager import DataManager

SCORE_MODES = ["客观", "主观", "总体"]
MODE_COLORS = ["#3498db", "#e67e22", "#1abc9c"]


class RadarCanvasWidget(QWidget):
    """QPainter 绘制的雷达图"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)
        self._cats: list[str] = []
        self._data: list[list[float]] = []
        self._data_old: list[list[float]] = []
        self._colors: list[tuple] = []
        self._anim_step = 10
        self._anim_token = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._anim_tick)
        self.setStyleSheet("background: white; border: 1px solid #ecf0f1; border-radius: 10px;")

    def set_data(self, cats: list[str], data: list[list[float]],
                 colors: list[tuple], animate: bool = False):
        if animate and self._data and len(self._data) == len(data):
            self._data_old = [list(d) for d in self._data]
            self._data = data
            self._cats = cats
            self._colors = colors
            self._anim_step = 0
            self._anim_token += 1
            self._timer.start(20)
        else:
            self._timer.stop()
            self._data = data
            self._data_old = []
            self._cats = cats
            self._colors = colors
            self._anim_step = 10
            self.update()

    def _anim_tick(self):
        self._anim_step += 1
        if self._anim_step >= 10:
            self._timer.stop()
            self._data_old = []
        self.update()

    def paintEvent(self, event):
        if not self._cats or not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        N = len(self._cats)
        if N < 3:
            return
        cx = self.width() / 2
        cy = self.height() / 2
        r = min(cx, cy) * 0.72

        t_eased = 1.0
        if self._data_old and self._anim_step < 10:
            t = (self._anim_step + 1) / 10
            t_eased = t * t * (3 - 2 * t)

        # 数据多边形（先画 fill，网格画在上面）
        for di, (vals, color) in enumerate(zip(self._data, self._colors)):
            if self._data_old and di < len(self._data_old):
                interp = [o + (n - o) * t_eased
                         for o, n in zip(self._data_old[di], vals)]
            else:
                interp = vals
            pts = []
            for i, v in enumerate(interp):
                angle = math.radians(90 - i * 360 / N)
                pts.append(QPointF(cx + r * v * math.cos(angle),
                                   cy - r * v * math.sin(angle)))
            if not pts:
                continue
            pts.append(pts[0])
            path = QPainterPath()
            path.addPolygon(QPolygonF(pts))
            p.fillPath(path, QBrush(QColor(*color)))
            p.setPen(QPen(QColor(color[0], color[1], color[2]), 2))
            p.drawPolyline(QPolygonF(pts))

        # 同心圆网格（画在 fill 之上，确保可见）
        p.setPen(QPen(QColor("#bdc3c7"), 1, Qt.PenStyle.DotLine))
        for level in [0.25, 0.50, 0.75, 1.0]:
            lr = r * level
            p.drawEllipse(QPointF(cx, cy), lr, lr)
        # 百分比刻度
        p.setPen(QPen(QColor("#95a5a6")))
        p.setFont(QFont("Microsoft YaHei", 8))
        for level in [0.25, 0.50, 0.75, 1.0]:
            p.drawText(QRectF(cx + 4, cy - r * level - 10, 40, 16),
                       Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                       f"{level:.0%}")
        # 轴线
        for i in range(N):
            angle = math.radians(90 - i * 360 / N)
            p.drawLine(QPointF(int(cx), int(cy)),
                       QPointF(int(cx + r * math.cos(angle)),
                               int(cy - r * math.sin(angle))))

        # 标签
        p.setPen(QPen(QColor("#2c3e50")))
        p.setFont(QFont("Microsoft YaHei", 9))
        for i, cat in enumerate(self._cats):
            angle = math.radians(90 - i * 360 / N)
            lx = cx + r * 1.18 * math.cos(angle)
            ly = cy - r * 1.18 * math.sin(angle)
            p.drawText(QRectF(lx - 40, ly - 10, 80, 20),
                       Qt.AlignmentFlag.AlignCenter, cat)
        p.end()


class RadarQPainterTab(QWidget):
    """QPainter 雷达图 — 实验页面"""

    def __init__(self, dm: DataManager):
        super().__init__()
        self.dm = dm
        self._current_student: str = ""
        self._score_mode: int = 0
        self._filter_start: str = ""
        self._filter_end: str = ""
        self._last_data_hash: int = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        toolbar.addWidget(QLabel("学生:"))
        self.combo_student = QComboBox()
        self.combo_student.setMinimumWidth(120)
        self.combo_student.setStyleSheet("""
            QComboBox { border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 4px 10px; font-size: 13px; background: white; color: #2c3e50; }
            QComboBox:hover { border-color: #1abc9c; }
        """)
        self.combo_student.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.combo_student)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索学生...")
        self.search_input.setStyleSheet("""
            QLineEdit { border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 4px 10px; font-size: 13px; background: white; color: #2c3e50;
                min-width: 100px; }
            QLineEdit:focus { border-color: #1abc9c; }
        """)
        self.search_input.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_input)

        toolbar.addSpacing(12)
        toolbar.addWidget(QLabel("分数模式:"))

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
        self.score_group.buttonClicked.connect(lambda: self.refresh())

        toolbar.addSpacing(12)

        # 测验/考试切换
        self.exam_type_btns: list[QPushButton] = []
        self.exam_type_group = QButtonGroup(self)
        for i, label in enumerate(["测验", "考试", "全部"]):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(i == 2)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(30)
            r_left = "8px" if i == 0 else "0px"
            r_right = "8px" if i == 2 else "0px"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white; border: 2px solid #95a5a6;
                    border-radius: {r_left} {r_right} {r_right} {r_left};
                    padding: 4px 12px; font-size: 12px; color: #636e72; font-weight: bold;
                }}
                QPushButton:hover {{ background: #ecf0f1; }}
                QPushButton:checked {{ background: #95a5a6; color: white; }}
            """)
            self.exam_type_group.addButton(btn, i)
            toolbar.addWidget(btn)
            self.exam_type_btns.append(btn)
        self.exam_type_group.buttonClicked.connect(lambda: self.refresh())

        # 固定顺序
        self.btn_fixed_order = QPushButton("📐 固定雷达图顺序")
        self.btn_fixed_order.setCheckable(True)
        self.btn_fixed_order.setChecked(True)
        self.btn_fixed_order.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fixed_order.setFixedHeight(30)
        self.btn_fixed_order.setStyleSheet("""
            QPushButton {
                background: transparent; border: 1px solid #bdc3c7; border-radius: 8px;
                padding: 4px 10px; font-size: 12px; color: #7f8c8d;
            }
            QPushButton:checked { background: #ecf0f1; color: #2c3e50; border-color: #bdc3c7; }
        """)
        self.btn_fixed_order.clicked.connect(lambda: self.refresh())
        toolbar.addWidget(self.btn_fixed_order)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 日期筛选行
        date_row = QHBoxLayout()
        date_row.setSpacing(8)
        date_row.addWidget(QLabel("起始:"))
        self.combo_start = QComboBox()
        self.combo_start.setMinimumWidth(100)
        self.combo_start.setStyleSheet("""
            QComboBox { border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 4px 10px; font-size: 13px; background: white; color: #2c3e50; }
            QComboBox:hover { border-color: #1abc9c; }
        """)
        self.combo_start.currentIndexChanged.connect(self._on_date_changed)
        date_row.addWidget(self.combo_start)
        date_row.addWidget(QLabel("截止:"))
        self.combo_end = QComboBox()
        self.combo_end.setMinimumWidth(100)
        self.combo_end.setStyleSheet(self.combo_start.styleSheet())
        self.combo_end.currentIndexChanged.connect(self._on_date_changed)
        date_row.addWidget(self.combo_end)
        self.btn_recent7 = QPushButton("📅 近7次")
        self.btn_recent7.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_recent7.setFixedHeight(30)
        self.btn_recent7.setStyleSheet("""
            QPushButton { background: #d5f5e3; border: none; border-radius: 8px;
                padding: 4px 14px; font-size: 12px; color: #1e8449; }
            QPushButton:hover { background: #a9dfbf; color: #145a32; }
        """)
        self.btn_recent7.clicked.connect(self._on_show_recent7)
        date_row.addWidget(self.btn_recent7)
        self.btn_all = QPushButton("↺ 全部")
        self.btn_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_all.setFixedHeight(30)
        self.btn_all.setStyleSheet("""
            QPushButton { background: #ecf0f1; border: none; border-radius: 8px;
                padding: 4px 14px; font-size: 12px; color: #636e72; }
            QPushButton:hover { background: #dfe6e9; color: #2d3436; }
        """)
        self.btn_all.clicked.connect(self._on_show_all)
        date_row.addWidget(self.btn_all)
        date_row.addStretch()
        layout.addLayout(date_row)

        self.canvas = RadarCanvasWidget()
        layout.addWidget(self.canvas, 1)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 2px 0; font-size: 12px;")
        layout.addWidget(self.status_label)

        self.refresh()

    # ------------------------------------------------------------------
    # 数据计算（与 student_eval_tab 一致）
    # ------------------------------------------------------------------
    def _compute_radar_data(self):
        student = self._current_student
        if not student:
            return [], [], []
        obj_perf = self._get_topic_rates("obj")
        sub_perf = self._get_topic_rates("sub")
        cat_obj, cat_sub = {}, {}
        for name, data in obj_perf.items():
            if data["rate"] is not None:
                cat_obj.setdefault(data["category"], []).append(data["rate"])
        for name, data in sub_perf.items():
            if data["rate"] is not None:
                cat_sub.setdefault(data["category"], []).append(data["rate"])
        for c in cat_obj:
            cat_obj[c] = round(sum(cat_obj[c]) / len(cat_obj[c]), 3)
        for c in cat_sub:
            cat_sub[c] = round(sum(cat_sub[c]) / len(cat_sub[c]), 3)
        use_fixed = self.btn_fixed_order.isChecked()
        if use_fixed:
            fixed_order = self.dm.category_order or list(self.dm.knowledge_pool.keys())
            all_cats = [c for c in fixed_order
                       if c in set(cat_obj.keys()) | set(cat_sub.keys())]
            extra = sorted(set(cat_obj.keys()) | set(cat_sub.keys()) - set(all_cats))
            all_cats += extra
        else:
            all_cats = sorted(
                set(cat_obj.keys()) | set(cat_sub.keys()),
                key=lambda c: cat_obj.get(c, 0) + cat_sub.get(c, 0),
                reverse=True,
            )
        return all_cats, [cat_obj.get(c, 0.0) for c in all_cats], [cat_sub.get(c, 0.0) for c in all_cats]

    def _get_topic_rates(self, qtype_filter):
        student = self._current_student
        class_idx = self.dm.current_class
        date_filter = self._get_filtered_dates()
        exam_type = self.exam_type_group.checkedId()
        if exam_type < 0:
            exam_type = 2
        topic_qlist: dict[str, list[tuple]] = {}
        for date, meta in self.dm.exam_meta.items():
            if date_filter and date not in date_filter:
                continue
            if exam_type != 2 and self.dm.is_quiz(date) != (exam_type == 0):
                continue
            if not meta.questions:
                continue
            for q in meta.questions:
                if qtype_filter == "obj" and q.qtype not in ("choice", "multi_select"):
                    continue
                if qtype_filter == "sub" and q.qtype not in ("fill", "answer"):
                    continue
                for kt in q.topics:
                    topic_qlist.setdefault(kt.name, []).append(
                        (date, q.id, q.max_score, kt.weight))
        topic_category = {}
        for cat, topics in self.dm.knowledge_pool.items():
            for t in topics:
                topic_category[t] = cat
        stu_obj = None
        for s in self.dm.students[class_idx][0]:
            if s.name == student:
                stu_obj = s
                break
        result = {}
        for tname, qlist in topic_qlist.items():
            s_sum = m_sum = 0.0
            for date, qid, max_score, weight in qlist:
                if stu_obj and date in stu_obj.question_scores:
                    qs = stu_obj.question_scores[date]
                    if qid in qs:
                        s_sum += qs[qid] * weight
                        m_sum += max_score * weight
            cat = topic_category.get(tname, "未分类")
            result[tname] = {"rate": round(s_sum / m_sum, 3) if m_sum > 0 else None,
                             "category": cat}
        return result

    # ------------------------------------------------------------------
    # 日期筛选
    # ------------------------------------------------------------------
    def _get_filtered_dates(self) -> set:
        if not self._filter_start and not self._filter_end:
            return set(self.dm.dates)
        result = set()
        for d in self.dm.dates:
            if self._filter_start and d < self._filter_start:
                continue
            if self._filter_end and d > self._filter_end:
                continue
            result.add(d)
        return result

    def _on_date_changed(self):
        self._filter_start = self.combo_start.currentText()
        self._filter_end = self.combo_end.currentText()
        self.refresh()

    def _on_show_all(self):
        self.combo_start.blockSignals(True)
        self.combo_end.blockSignals(True)
        self.combo_start.setCurrentIndex(self.combo_start.count() - 1)
        self.combo_end.setCurrentIndex(0)
        self.combo_start.blockSignals(False)
        self.combo_end.blockSignals(False)
        self._filter_start = ""
        self._filter_end = ""
        self.refresh()

    def _on_show_recent7(self):
        dates = self.dm.dates
        if not dates:
            return
        n = min(7, len(dates))
        self.combo_start.blockSignals(True)
        self.combo_end.blockSignals(True)
        self.combo_end.setCurrentIndex(0)
        self.combo_start.setCurrentIndex(n - 1)
        self.combo_start.blockSignals(False)
        self.combo_end.blockSignals(False)
        self._filter_start = dates[-n]
        self._filter_end = dates[-1]
        self.refresh()

    # ------------------------------------------------------------------
    def _on_search(self, text: str):
        for i in range(self.combo_student.count()):
            if text.lower() in self.combo_student.itemText(i).lower():
                self.combo_student.setCurrentIndex(i)
                return

    def refresh(self):
        self._current_student = self.combo_student.currentText()
        self._score_mode = self.score_group.checkedId()
        if self._score_mode < 0:
            self._score_mode = 0
        students = self.dm.current_students
        if not students:
            return

        # 初始化日期下拉（首次或日期变更时）
        dates = self.dm.dates
        if dates and (self.combo_start.count() == 0 or
                      self.combo_start.itemText(0) != dates[-1]):
            self.combo_start.blockSignals(True)
            self.combo_end.blockSignals(True)
            self.combo_start.clear()
            self.combo_end.clear()
            reversed_dates = list(reversed(dates))
            self.combo_start.addItems(reversed_dates)
            self.combo_end.addItems(reversed_dates)
            self.combo_end.setCurrentIndex(0)
            try:
                last_dt = datetime.strptime(dates[-1], "%Y/%m/%d")
                week_ago = last_dt - timedelta(days=7)
                week_ago_str = week_ago.strftime("%Y/%m/%d")
                start_idx = 0
                for i, d in enumerate(dates):
                    if d >= week_ago_str:
                        start_idx = i
                        break
                rev_start_idx = len(dates) - 1 - start_idx
                self.combo_start.setCurrentIndex(rev_start_idx)
                self._filter_start = dates[start_idx]
            except ValueError:
                self.combo_start.setCurrentIndex(len(dates) - 1)
                self._filter_start = dates[0]
            self._filter_end = dates[-1]
            self.combo_start.blockSignals(False)
            self.combo_end.blockSignals(False)

        current = self.combo_student.currentText()
        self.combo_student.blockSignals(True)
        self.combo_student.clear()
        names = sorted([s.name for s in students])
        self.combo_student.addItems(names)
        completer = QCompleter(names)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_input.setCompleter(completer)
        if current and current in names:
            self.combo_student.setCurrentText(current)
        elif names:
            self.combo_student.setCurrentText(names[0])
            self._current_student = names[0]
        self.combo_student.blockSignals(False)

        all_cats, obj_vals, sub_vals = self._compute_radar_data()
        N = len(all_cats)
        if N < 3:
            self.status_label.setText("类别数量不足3个，请先在数据维护页绑定知识点到题目。")
            self.canvas.set_data([], [], [])
            return

        if self._score_mode == 0:
            data = [obj_vals]
            colors = [(52, 152, 219, 80)]
        elif self._score_mode == 1:
            data = [sub_vals]
            colors = [(230, 126, 34, 80)]
        else:
            data = [obj_vals, sub_vals]
            colors = [(52, 152, 219, 60), (230, 126, 34, 60)]

        data_hash = hash((N, self._score_mode, tuple(round(v, 3) for vals in data for v in vals)))
        animate = (self._last_data_hash != 0 and data_hash != self._last_data_hash)
        self._last_data_hash = data_hash
        self.canvas.set_data(all_cats, data, colors, animate=animate)

        if self._score_mode == 0:
            vals = obj_vals
        elif self._score_mode == 1:
            vals = sub_vals
        else:
            vals = [(o + s) / 2 for o, s in zip(obj_vals, sub_vals)]
        best_idx = max(range(N), key=lambda i: vals[i])
        worst_idx = min(range(N), key=lambda i: vals[i])
        self.status_label.setText(
            f"雷达图：{N} 个类别 | 最强: {all_cats[best_idx]}({vals[best_idx]:.0%}) | "
            f"最弱: {all_cats[worst_idx]}({vals[worst_idx]:.0%})"
        )
