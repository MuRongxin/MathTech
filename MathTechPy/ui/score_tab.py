"""成绩分析页 - 多种图表模式

图表模式：
1. 成绩分布 - 直方图显示班级分数段分布
2. 个人趋势 - 选择学生，显示历次考试成绩折线
3. 最近一次 - 柱状图显示最近一次考试全班成绩
4. 最近7次 - 折线图显示最近7次考试的班级平均分趋势
5. 目标分对比 - 对比当前分与目标分差距

修复的 C# bug / 本页修复：
1. 切换模式时正确更新控件可见性
2. 分页按钮带边界保护（越界回绕）
3. 空数据时显示友好提示而非空白/崩溃
4. 添加客观分/满分模式切换
5. 刷新时按需更新控件，避免冗余信号
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QSpinBox, QLineEdit, QGroupBox, QSlider, QCompleter, QButtonGroup
)
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.data_manager import DataManager


class ScoreTab(QWidget):
    MODE_DISTRIBUTION = "📊 成绩分布"
    MODE_PERSONAL = "👤 个人趋势"
    MODE_LATEST = "📋 最近一次"
    MODE_LAST7 = "📈 进退步榜"
    MODE_TARGET = "🎯 目标分对比"

    def __init__(self, dm: DataManager):
        super().__init__()
        self.dm = dm
        self._current_mode = self.MODE_DISTRIBUTION
        self._exam_index = -1
        self._display_count = 8
        self._group_offset = 0
        self._hover_annot = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ===== 第一行：全局控件 =====
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        row1.addWidget(QLabel("图表模式:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems([
            self.MODE_DISTRIBUTION,
            self.MODE_PERSONAL,
            self.MODE_LATEST,
            self.MODE_LAST7,
            self.MODE_TARGET,
        ])
        self.combo_mode.currentTextChanged.connect(self.on_mode_changed)
        row1.addWidget(self.combo_mode)

        row1.addSpacing(16)

        row1.addWidget(QLabel("🔍"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索学生姓名...")
        self.search_input.setMinimumWidth(140)
        self.search_input.setMaximumWidth(200)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 6px 10px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #1abc9c; }
        """)
        self.search_completer = QCompleter()
        self.search_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.search_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.search_input.setCompleter(self.search_completer)
        self.search_input.returnPressed.connect(self._on_search)
        self.search_completer.activated.connect(self._on_search)
        row1.addWidget(self.search_input)

        row1.addSpacing(16)

        # 题型分数切换
        self._score_type = "total"  # choice / fill / answer / total
        type_btns_layout = QHBoxLayout()
        type_btns_layout.setSpacing(0)
        type_colors = {"choice": "#3498db", "fill": "#e67e22", "answer": "#9b59b6", "total": "#1abc9c"}
        type_labels = {"choice": "选择题", "fill": "填空题", "answer": "解答题", "total": "总分"}
        self._type_btns: dict[str, QPushButton] = {}
        types = ["choice", "fill", "answer", "total"]
        for i, t in enumerate(types):
            btn = QPushButton(type_labels[t])
            btn.setCheckable(True)
            btn.setChecked(t == "total")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(32)
            c = type_colors[t]
            r_left = "8px" if i == 0 else "0px"
            r_right = "8px" if i == 3 else "0px"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white; color: {c};
                    border: 2px solid {c};
                    border-radius: {r_left} {r_right} {r_right} {r_left};
                    padding: 4px 14px; font-size: 12px; font-weight: bold;
                }}
                QPushButton:hover {{ background: #ecf0f1; }}
                QPushButton:checked {{ background: {c}; color: white; }}
            """)
            btn.clicked.connect(lambda checked, tt=t: self.switch_score_type(tt))
            type_btns_layout.addWidget(btn)
            self._type_btns[t] = btn
        row1.addLayout(type_btns_layout)

        row1.addStretch()

        # 测验/考试切换
        self.exam_type_btns: dict[str, QPushButton] = {}
        self.exam_type_group = QButtonGroup(self)
        self._exam_type = 2  # 0=quiz, 1=exam, 2=all
        for i, label in enumerate(["测验", "考试", "全部"]):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(i == 2)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(30)
            r_left = "8px" if i == 0 else "0px"
            r_right = "8px" if i == 2 else "0px"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white; border: 2px solid #95a5a6;
                    border-radius: {r_left} {r_right} {r_right} {r_left};
                    padding: 4px 10px; font-size: 12px; color: #636e72; font-weight: bold;
                }}
                QPushButton:hover {{ background: #ecf0f1; }}
                QPushButton:checked {{ background: #95a5a6; color: white; }}
            """)
            self.exam_type_group.addButton(btn, i)
            row1.addWidget(btn)
            self.exam_type_btns[label] = btn
        self.exam_type_group.buttonClicked.connect(self._on_exam_type_changed)

        layout.addLayout(row1)

        # ===== 第二行：上下文控件（按模式显示） =====
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        # 成绩分布：考试日期
        self.lbl_exam = QLabel("考试:")
        row2.addWidget(self.lbl_exam)
        self.btn_exam_prev = QPushButton("◀")
        self.btn_exam_prev.setFixedWidth(36)
        self.btn_exam_prev.clicked.connect(self._prev_exam)
        row2.addWidget(self.btn_exam_prev)
        self.slider_exam = QSlider(Qt.Orientation.Horizontal)
        self.slider_exam.setMinimumWidth(180)
        self.slider_exam.setMaximumWidth(320)
        self.slider_exam.valueChanged.connect(self._on_slider_changed)
        row2.addWidget(self.slider_exam)
        self.btn_exam_next = QPushButton("▶")
        self.btn_exam_next.setFixedWidth(36)
        self.btn_exam_next.clicked.connect(self._next_exam)
        row2.addWidget(self.btn_exam_next)
        self.lbl_exam_date = QLabel("")
        self.lbl_exam_date.setMinimumWidth(100)
        self.lbl_exam_date.setStyleSheet("color: #2c3e50; font-weight: bold;")
        row2.addWidget(self.lbl_exam_date)
        self._dist_ctrls = [self.lbl_exam, self.btn_exam_prev, self.slider_exam,
                            self.btn_exam_next, self.lbl_exam_date]

        # 个人趋势：学生 + 最近7次
        self.lbl_student = QLabel("学生:")
        row2.addWidget(self.lbl_student)
        self.combo_student = QComboBox()
        self.combo_student.setMinimumWidth(130)
        self.combo_student.currentIndexChanged.connect(self.refresh)
        row2.addWidget(self.combo_student)
        self.chk_last7 = QPushButton("📅 仅最近7次")
        self.chk_last7.setCheckable(True)
        self.chk_last7.setChecked(False)
        self.chk_last7.clicked.connect(self.refresh)
        row2.addWidget(self.chk_last7)
        self._personal_ctrls = [self.lbl_student, self.combo_student, self.chk_last7]

        # 最近一次 & 目标对比：显示人数 + 翻页
        self.lbl_count = QLabel("显示人数:")
        row2.addWidget(self.lbl_count)
        self.spin_count = QSpinBox()
        self.spin_count.setRange(5, 100)
        self.spin_count.setValue(15)
        self.spin_count.valueChanged.connect(self.on_count_changed)
        row2.addWidget(self.spin_count)
        self.btn_prev = QPushButton("◀ 上一组")
        self.btn_prev.clicked.connect(self.prev_group)
        row2.addWidget(self.btn_prev)
        self.btn_next = QPushButton("下一组 ▶")
        self.btn_next.clicked.connect(self.next_group)
        row2.addWidget(self.btn_next)
        self._paged_ctrls = [self.lbl_count, self.spin_count, self.btn_prev, self.btn_next]

        # 目标分对比：目标分输入
        self.lbl_target = QLabel("目标分:")
        row2.addWidget(self.lbl_target)
        self.edit_target = QLineEdit("0")
        self.edit_target.setMaximumWidth(55)
        self.edit_target.textChanged.connect(self.refresh)
        row2.addWidget(self.edit_target)
        self._target_ctrls = [self.lbl_target, self.edit_target]

        # 最近一次也需要分页控件，所以 _paged_ctrls 已覆盖；目标分需要分页+目标输入
        # 最近7次不需要 row2 控件

        row2.addStretch()
        layout.addLayout(row2)

        # ---------- 图表区 ----------
        self.fig = Figure(figsize=(10, 8.5), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)
        layout.addWidget(self.canvas)

        # ---------- 状态栏 ----------
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(self.status_label)

        # 初始化控件可见性
        self._update_toolbar_visibility()
        self.refresh()

    def on_mode_changed(self, mode: str):
        self._current_mode = mode
        self._group_offset = 0
        self._update_toolbar_visibility()
        self.refresh()

    def on_count_changed(self, val: int):
        self._display_count = val
        self._group_offset = 0
        self.refresh()

    def switch_score_type(self, stype: str):
        """切换题型分数：choice/fill/answer/total"""
        self._score_type = stype
        for t, btn in self._type_btns.items():
            btn.setChecked(t == stype)
        self.refresh()

    def _on_exam_type_changed(self):
        self._exam_type = self.exam_type_group.checkedId()
        self.refresh()

    def _filter_dates(self):
        """返回符合测验/考试筛选的日期列表"""
        et = self._exam_type if hasattr(self, '_exam_type') else 2
        if et == 2:
            return self.dm.dates
        return [dt for dt in self.dm.dates if self.dm.is_quiz(dt) == (et == 0)]

    def _get_typed_scores(self, students, date_idx: int = -1):
        """按当前题型过滤，返回 [(name, score), ...]"""
        if not self.dm.dates:
            return []
        stype = self._score_type
        result = []
        for s in students:
            if stype == "total":
                # date-keyed lookup 避免缺考错位
                score_map = {d: float(v) for d, v in (s.scores_full or s.scores or [])}
                if not self.dm.dates:
                    continue
                dt_idx = date_idx if 0 <= date_idx < len(self.dm.dates) else len(self.dm.dates) - 1
                if 0 <= dt_idx < len(self.dm.dates):
                    dt = self.dm.dates[dt_idx]
                    if dt in score_map:
                        result.append((s.name, score_map[dt]))
            else:
                # 按题型汇总逐题分
                qtype_filter = {"choice": ("choice", "multi_select"),
                                "fill": ("fill",),
                                "answer": ("answer",)}[stype]
                # 取指定考试日期的逐题分
                if not self.dm.dates:
                    continue
                idx = date_idx if 0 <= date_idx < len(self.dm.dates) else len(self.dm.dates) - 1
                dt = self.dm.dates[idx]
                meta = self.dm.get_exam_meta(dt)
                if not meta.questions:
                    continue
                total = 0.0
                for q in meta.questions:
                    if q.qtype in qtype_filter and dt in s.question_scores:
                        total += s.question_scores[dt].get(q.id, 0.0)
                if total > 0 or s.question_scores.get(dt):
                    result.append((s.name, round(total, 1)))
        return result

    def _update_toolbar_visibility(self):
        """根据模式显示/隐藏第二行控件"""
        is_dist = self._current_mode == self.MODE_DISTRIBUTION
        is_personal = self._current_mode == self.MODE_PERSONAL
        is_paged = self._current_mode in (self.MODE_LATEST, self.MODE_TARGET, self.MODE_LAST7)
        is_target = self._current_mode == self.MODE_TARGET

        for c in self._dist_ctrls:
            c.setVisible(is_dist)
        for c in self._personal_ctrls:
            c.setVisible(is_personal)
        for c in self._paged_ctrls:
            c.setVisible(is_paged)
        for c in self._target_ctrls:
            c.setVisible(is_target)

    def _on_hover(self, event):
        """鼠标悬停显示考试日期和成绩"""
        if not event.inaxes:
            if self._hover_annot:
                self._hover_annot.set_visible(False)
                self.canvas.draw_idle()
            return

        ax = event.inaxes
        dates = getattr(self, "_hover_dates", [])
        raw = getattr(self, "_hover_raw", [])
        best_dist = float("inf")
        best_info = None
        best_xy = None

        for line in ax.lines:
            xdata, ydata = line.get_data()
            if len(xdata) == 0:
                continue
            pts = ax.transData.transform(list(zip(xdata, ydata)))
            for i, (px, py) in enumerate(pts):
                dist = ((px - event.x) ** 2 + (py - event.y) ** 2) ** 0.5
                if dist < best_dist:
                    best_dist = dist
                    idx = int(xdata[i])
                    date_str = dates[idx] if 0 <= idx < len(dates) else f"第{idx+1}次"
                    label = line.get_label()
                    info = f"{date_str}  {ydata[i]:.2f}"
                    if label and not label.startswith("_"):
                        info = f"{label}\n{info}"
                    # Z 分图附上原始分
                    if raw and 0 <= idx < len(raw):
                        info += f"\n原始分 {raw[idx]:.1f}"
                    best_info = info
                    best_xy = (xdata[i], ydata[i])

        if best_dist > 15 or best_xy is None:
            if self._hover_annot:
                self._hover_annot.set_visible(False)
                self.canvas.draw_idle()
            return

        # 跨子图切换时重建 annot
        if self._hover_annot and self._hover_annot.axes != ax:
            self._hover_annot.remove()
            self._hover_annot = None

        if self._hover_annot is None:
            self._hover_annot = ax.annotate(
                "", xy=best_xy, xytext=(14, 14),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.6", facecolor="#2c3e50",
                          edgecolor="none", alpha=0.92),
                color="white", fontsize=11,
                arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1.2),
            )
        else:
            self._hover_annot.xy = best_xy

        self._hover_annot.set_text(best_info)
        self._hover_annot.set_visible(True)
        self.canvas.draw_idle()

    def refresh(self):
        """刷新图表"""
        students = self.dm.current_students
        if not students:
            self._show_empty("当前班级没有学生数据")
            return

        # 更新日期滑块范围（成绩分布模式）
        if self._current_mode == self.MODE_DISTRIBUTION and self.dm.dates:
            n = len(self.dm.dates)
            self.slider_exam.blockSignals(True)
            self.slider_exam.setRange(0, n - 1)
            if self._exam_index < 0 or self._exam_index >= n:
                self._exam_index = n - 1
            self.slider_exam.setValue(self._exam_index)
            self._update_exam_label()
            self.slider_exam.blockSignals(False)

        # 只在个人模式需要时更新学生下拉框
        if self._current_mode in (self.MODE_PERSONAL,):
            current_name = self.combo_student.currentText()
            self.combo_student.blockSignals(True)
            self.combo_student.clear()
            for s in students:
                self.combo_student.addItem(s.name)
            if current_name:
                idx = self.combo_student.findText(current_name)
                if idx >= 0:
                    self.combo_student.setCurrentIndex(idx)
            self.combo_student.blockSignals(False)

        # 始终更新搜索补全的模型
        names = [s.name for s in students]
        model = QStringListModel(names)
        self.search_completer.setModel(model)

        self._hover_annot = None
        self.fig.clear()
        try:
            if self._current_mode == self.MODE_DISTRIBUTION:
                self._draw_distribution(students)
            elif self._current_mode == self.MODE_PERSONAL:
                self._draw_personal(students)
            elif self._current_mode == self.MODE_LATEST:
                self._draw_latest(students)
            elif self._current_mode == self.MODE_LAST7:
                self._draw_last7(students)
            elif self._current_mode == self.MODE_TARGET:
                self._draw_target(students)
        except Exception as e:
            self._show_error(str(e))

        self.fig.tight_layout(pad=2.0, h_pad=1.5, w_pad=1.0)
        self.canvas.draw()

    def _get_paged_data(self, data: list) -> list:
        """分页读取，带越界回绕保护"""
        if not data:
            return []
        total = len(data)
        # 确保 offset 在有效范围内
        self._group_offset = self._group_offset % total if total > 0 else 0
        start = self._group_offset
        end = min(start + self._display_count, total)
        return data[start:end]

    def _show_empty(self, msg: str):
        """显示空数据提示"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, msg, ha="center", va="center",
                fontsize=16, color="#95a5a6", transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        self.status_label.setText(msg)

    def _show_error(self, msg: str):
        """显示错误信息"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.text(0.5, 0.5, f"绘图出错:\n{msg}", ha="center", va="center",
                fontsize=12, color="#e74c3c", transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        self.status_label.setText(f"错误: {msg}")

    # ------------------------------------------------------------------
    # 图表绘制
    # ------------------------------------------------------------------
    def _draw_distribution(self, students):
        """成绩分布直方图"""
        exam_idx = self.slider_exam.value()
        if exam_idx < 0:
            exam_idx = len(self.dm.dates) - 1

        data = self._get_typed_scores(students, exam_idx)
        if not data:
            self._show_empty("无成绩数据（该题型可能无逐题分）")
            return
        scores = [s for _, s in data]

        ax = self.fig.add_subplot(111)

        # 用最大值做归一化
        max_sc = max(scores) if scores else 100
        props = [sc / max_sc for sc in scores] if max_sc > 0 else [0] * len(scores)

        bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        labels = ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%",
                  "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]
        counts = [0] * (len(bins) - 1)
        for p in props:
            for i in range(len(bins) - 1):
                if bins[i] <= p < bins[i + 1] or (i == len(bins) - 2 and p == bins[i + 1]):
                    counts[i] += 1
                    break

        colors = ["#c0392b", "#e74c3c", "#e67e22", "#d68910", "#f1c40f",
                  "#7cb342", "#2ecc71", "#1abc9c", "#17a589", "#138d75"]
        bars = ax.bar(labels, counts, color=colors, edgecolor="white", width=0.6)

        for bar, cnt in zip(bars, counts):
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5,
                        str(cnt), ha="center", va="bottom", fontsize=12, fontweight="bold")

        type_name = {"choice": "选择题", "fill": "填空题", "answer": "解答题", "total": "总分"}[self._score_type]
        exam_date = self.dm.dates[exam_idx] if exam_idx < len(self.dm.dates) else "未知"
        ax.set_ylabel("人数", fontsize=12)
        ax.set_xlabel("得分率分段", fontsize=12)
        ax.set_title(f"成绩分布 ({type_name}, {exam_date}, n={len(props)})", fontsize=14, fontweight="bold")
        ax.set_ylim(0, max(max(counts) * 1.2, 10))

        self._hover_dates = self.dm.dates
        self.status_label.setText(
            f"日期: {exam_date}  |  平均分: {sum(scores)/len(scores):.1f}  |  "
            f"最高分: {max(scores):.1f}  |  最低分: {min(scores):.1f}  |  {type_name}"
        )

    def _draw_personal(self, students):
        """个人成绩趋势 — 按题型过滤的逐次考试得分"""
        name = self.combo_student.currentText()
        if not name:
            self._show_empty("请从下拉框选择学生")
            return

        # 收集该学生所有考试的题型得分 + 理论满分
        stype = self._score_type
        qtype_filter = {"choice": ("choice", "multi_select"),
                        "fill": ("fill",), "answer": ("answer",)}.get(stype, None)
        dates, rates, class_rates = [], [], []
        filtered_dates = self._filter_dates()
        for exam_i, dt in enumerate(self.dm.dates):
            if dt not in filtered_dates:
                continue
            data = self._get_typed_scores(students, exam_i)
            if not data:
                continue
            sd = dict(data)
            if name not in sd:
                continue
            meta = self.dm.get_exam_meta(dt)
            if meta.questions:
                if qtype_filter:
                    max_score = sum(q.max_score for q in meta.questions
                                    if q.qtype in qtype_filter)
                else:
                    max_score = sum(q.max_score for q in meta.questions)
            else:
                max_score = max(v for _, v in data) if data else 100.0
            if max_score <= 0:
                continue
            dates.append(dt)
            rates.append(round(sd[name] / max_score, 4))
            class_rates.append(round(sum(v for _, v in data) / len(data) / max_score, 4))

        if not rates:
            self._show_empty(f"{name} 无该题型成绩数据")
            return

        is_last7 = self.chk_last7.isChecked()
        if is_last7:
            n = min(7, len(rates))
            dates = dates[-n:]
            rates = rates[-n:]
            class_rates = class_rates[-n:]

        n_pts = len(rates)
        step = max(1, n_pts // 8)
        tick_pos = list(range(0, n_pts, step))
        x = list(range(n_pts))

        ax = self.fig.add_subplot(111)
        ax.plot(x, rates, marker="o", linewidth=2.5,
                color="#8e44ad", markersize=7, zorder=3, label=name)
        ax.plot(x, class_rates, color="#e74c3c", linestyle="--", linewidth=2.2,
                label="班级平均得分率", zorder=4, alpha=0.9)

        ax.set_ylim(-0.05, 1.05)
        ax.axhline(y=0.5, color="#999", linewidth=0.8, linestyle="--", alpha=0.5)

        type_name = {"choice": "选择题", "fill": "填空题", "answer": "解答题", "total": "总分"}[self._score_type]
        title = f"{name} — {type_name}得分率" + (" (最近7次)" if is_last7 else f" (共{n_pts}次)")
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_ylabel("得分率", fontsize=11)
        ax.legend(fontsize=9, loc="upper left")
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.set_xticks(tick_pos)
        ax.set_xticklabels([dates[i] for i in tick_pos], rotation=45, ha="right")

        if is_last7:
            for xi, r in zip(x, rates):
                ax.text(xi, r + 0.03, f"{r:.0%}", ha="center", fontsize=8, color="#8e44ad")

        self._hover_dates = dates
        self._hover_raw = rates
        avg = sum(rates) / n_pts
        self.status_label.setText(
            f"{name} | {type_name} | {'最近7次' if is_last7 else f'共{n_pts}次'} | "
            f"均得分率 {avg:.0%} | "
            f"最高 {max(rates):.0%} | 最低 {min(rates):.0%}"
        )

    def _draw_latest(self, students):
        """最近一次考试柱状图 — 按题型分数排序"""
        fdates = self._filter_dates()
        if not fdates:
            self._show_empty("无符合筛选条件的考试")
            return
        latest_idx = self.dm.dates.index(fdates[-1])
        data = self._get_typed_scores(students, latest_idx)
        if not data:
            self._show_empty("无该题型成绩数据")
            return

        data.sort(key=lambda x: x[1], reverse=True)
        page_data = self._get_paged_data(data)
        if not page_data:
            self._group_offset = 0
            page_data = self._get_paged_data(data)

        names = [d[0] for d in page_data]
        scores = [d[1] for d in page_data]
        total = len(data)
        start = self._group_offset + 1
        end = min(self._group_offset + len(page_data), total)

        ax = self.fig.add_subplot(111)
        colors = ["#3498db" for _ in scores]
        ax.barh(range(len(names)), scores, color=colors, height=0.6)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.invert_yaxis()
        max_sc = max(scores) if scores else 100
        ax.set_xlim(0, max_sc * 1.2)

        class_avg = sum(v for _, v in data) / len(data) if data else 0
        ax.axvline(x=class_avg, color="#e74c3c", linewidth=1.5, linestyle="--", alpha=0.7)
        ax.text(class_avg + 0.5, len(names) - 0.5, f"全班均{class_avg:.1f}",
                color="#e74c3c", fontsize=9, fontweight="bold")
        for i, sc in enumerate(scores):
            ax.text(sc + 0.3, i, f"{sc:.1f}", va="center", fontsize=8)

        type_name = {"choice": "选择题", "fill": "填空题", "answer": "解答题", "total": "总分"}[self._score_type]
        ax.set_xlabel(f"{type_name}得分", fontsize=11)
        ax.set_title(f"最近一次考试 ({type_name}) 第 {start}-{end} / {total} 名", fontsize=13, fontweight="bold")

        self.status_label.setText(
            f"共 {total} 人 | 显示第 {start}-{end} 名 | {type_name}"
        )

    def _draw_last7(self, students):
        """进退步榜：最近 N 次考试题型得分变化"""
        fdates = self._filter_dates()
        n = min(7, len(fdates))
        if n < 2:
            self._show_empty("考试次数不足")
            return

        dates = fdates[-n:]
        changes = []
        for s in students:
            scores_n = []
            for dt in dates:
                exam_i = self.dm.dates.index(dt)
                data = self._get_typed_scores(students, exam_i)
                sd = dict(data) if data else {}
                if s.name not in sd:
                    continue  # 缺考不参与趋势计算
                scores_n.append(sd[s.name])
            if len(scores_n) >= 2:
                k = len(scores_n)
                mx = (k - 1) / 2
                my = sum(scores_n) / k
                num = sum((i - mx) * (scores_n[i] - my) for i in range(k))
                den = sum((i - mx) ** 2 for i in range(k))
                slope = num / den if den != 0 else 0
                diff = slope * (k - 1)
                changes.append((s.name, diff, scores_n[0], scores_n[-1]))

        if not changes:
            self._show_empty("数据不足")
            return

        changes.sort(key=lambda x: x[1], reverse=True)
        total = len(changes)
        self._group_offset = self._group_offset % total if total > 0 else 0
        start = self._group_offset
        end = min(start + self._display_count, total)
        page = changes[start:end]

        names = [c[0] for c in page]
        diffs = [c[1] for c in page]
        firsts = [c[2] for c in page]
        lasts = [c[3] for c in page]

        ax = self.fig.add_subplot(111)
        colors = ["#2ecc71" if d >= 0 else "#e74c3c" for d in diffs]
        ax.barh(range(len(names)), diffs, color=colors, height=0.7, edgecolor="white")

        for i, (d, fv, lv) in enumerate(zip(diffs, firsts, lasts)):
            sign = "+" if d >= 0 else ""
            text = f"{sign}{d:.1f}  ({fv:.1f} → {lv:.1f})"
            offset = max(abs(d) * 0.02, 0.5)
            x_pos = d + offset if d >= 0 else d - offset
            ha = "left" if d >= 0 else "right"
            ax.text(x_pos, i, text, va="center", ha=ha, fontsize=10)

        base = max(abs(min(diffs)), abs(max(diffs)), 1.0)
        ax.set_xlim(-base * 1.5, base * 1.5)
        ax.axvline(x=0, color="#999", linewidth=0.8, alpha=0.5)
        ax.spines["right"].set_visible(False)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=10)
        ax.invert_yaxis()

        type_name = {"choice": "选择题", "fill": "填空题", "answer": "解答题", "total": "总分"}[self._score_type]
        ax.set_xlabel(f"{type_name}得分变化", fontsize=12)
        ax.set_title(f"最近 {n} 次考试进退步榜 ({dates[0]} → {dates[-1]}) "
                     f"第 {start+1}-{end}/{total} 名 | {type_name}",
                     fontsize=13, fontweight="bold")

        up = sum(1 for d in diffs if d >= 0)
        down = len(diffs) - up
        self._hover_dates = []
        self.status_label.setText(
            f"最近{n}次 | 进步 {up} 人 | 退步 {down} 人 | "
            f"最大进步 {max(diffs):.1f} | 最大退步 {min(diffs):.1f} | {type_name}"
        )

    def _draw_target(self, students):
        """目标分对比 — 最新一次考试的题型得分距目标分差距"""
        try:
            target = float(self.edit_target.text())
        except ValueError:
            target = 0

        fdates = self._filter_dates()
        if not fdates:
            self._show_empty("无符合筛选条件的考试")
            return
        latest_idx = self.dm.dates.index(fdates[-1])
        data = self._get_typed_scores(students, latest_idx)
        if not data:
            self._show_empty("无该题型成绩数据")
            return

        # 计算与目标分的差距
        gap_data = [(name, score, score - target) for name, score in data]
        gap_data.sort(key=lambda x: x[2], reverse=True)

        total = len(gap_data)
        self._group_offset = self._group_offset % total if total > 0 else 0
        start = self._group_offset
        end = min(start + self._display_count, total)
        page = gap_data[start:end]

        names = [d[0] for d in page]
        gaps = [d[2] for d in page]

        ax = self.fig.add_subplot(111)
        colors = ["#2ecc71" if d >= 0 else "#e74c3c" for d in gaps]
        ax.barh(range(len(names)), gaps, color=colors, height=0.6)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.invert_yaxis()
        ax.axvline(x=0, color="#e74c3c", linewidth=1.5, alpha=0.8,
                    label=f"目标分={target:.1f}")
        ax.legend(fontsize=11, loc="lower right")

        for i, d in enumerate(gaps):
            sign = "+" if d >= 0 else ""
            ax.text(d + 0.3 if d >= 0 else d - 0.3, i, f"{sign}{d:.1f}",
                    va="center", ha="left" if d >= 0 else "right", fontsize=8)

        type_name = {"choice": "选择题", "fill": "填空题", "answer": "解答题", "total": "总分"}[self._score_type]
        ax.set_xlabel(f"{type_name}得分差距", fontsize=11)
        ax.set_title(f"目标分对比 ({type_name}) 第 {start+1}-{end}/{total} 名",
                     fontsize=13, fontweight="bold")

        above = sum(1 for d in gaps if d >= 0)
        self.status_label.setText(
            f"目标分={target:.1f} | 达标{above}/{len(gaps)} | {type_name}"
        )

    # ------------------------------------------------------------------
    # 分页
    # ------------------------------------------------------------------
    def prev_group(self):
        students = self.dm.current_students
        data = self._get_typed_scores(students)
        if not data:
            return
        total = len(data)
        self._group_offset = (self._group_offset - self._display_count) % total
        self.refresh()

    def next_group(self):
        students = self.dm.current_students
        data = self._get_typed_scores(students)
        if not data:
            return
        total = len(data)
        self._group_offset = (self._group_offset + self._display_count) % total
        self.refresh()

    # ------------------------------------------------------------------
    # 学生搜索
    # ------------------------------------------------------------------
    def _on_search(self):
        """搜索框回车或被选择：切到个人趋势模式并选中该学生"""
        text = self.search_input.text().strip()
        if not text:
            return

        # 用补全模型精确匹配（支持部分匹配）
        model = self.search_completer.model()
        if model:
            for row in range(model.rowCount()):
                idx = model.index(row, 0)
                name = model.data(idx)
                if name and text.lower() in name.lower():
                    text = name
                    break

        # 切到个人模式
        if self._current_mode != self.MODE_PERSONAL:
            self.combo_mode.setCurrentText(self.MODE_PERSONAL)
            self._current_mode = self.MODE_PERSONAL
            self._update_toolbar_visibility()

        # 选中学生
        idx = self.combo_student.findText(text)
        if idx >= 0:
            self.combo_student.setCurrentIndex(idx)
        self.refresh()

    # ------------------------------------------------------------------
    # 考试日期导航
    # ------------------------------------------------------------------
    def _prev_exam(self):
        val = self.slider_exam.value()
        if val > self.slider_exam.minimum():
            self.slider_exam.setValue(val - 1)

    def _next_exam(self):
        val = self.slider_exam.value()
        if val < self.slider_exam.maximum():
            self.slider_exam.setValue(val + 1)

    def _on_slider_changed(self, val: int):
        self._exam_index = val
        self._update_exam_label()
        self.refresh()

    def _update_exam_label(self):
        idx = self.slider_exam.value()
        if 0 <= idx < len(self.dm.dates):
            self.lbl_exam_date.setText(self.dm.dates[idx])
