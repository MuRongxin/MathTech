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
    QPushButton, QSpinBox, QLineEdit, QGroupBox, QSlider, QCompleter
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

    def __init__(self, dm: DataManager, on_mode_change=None):
        super().__init__()
        self.dm = dm
        self._on_mode_change = on_mode_change
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

        # 成绩模式切换
        self.btn_obj = QPushButton("仅客观分")
        self.btn_obj.setCheckable(True)
        self.btn_obj.clicked.connect(lambda: self.switch_score_mode(False))
        row1.addWidget(self.btn_obj)

        self.btn_full = QPushButton("整卷分")
        self.btn_full.setCheckable(True)
        self.btn_full.setChecked(True)
        self.btn_full.clicked.connect(lambda: self.switch_score_mode(True))
        row1.addWidget(self.btn_full)

        row1.addStretch()
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
        self.lbl_target_z = QLabel("目标Z:")
        row2.addWidget(self.lbl_target_z)
        self.edit_target_z = QLineEdit("0")
        self.edit_target_z.setMaximumWidth(55)
        self.edit_target_z.textChanged.connect(self.refresh)
        row2.addWidget(self.edit_target_z)
        self.lbl_target_raw = QLabel("目标分:")
        row2.addWidget(self.lbl_target_raw)
        self.edit_target_raw = QLineEdit("0")
        self.edit_target_raw.setMaximumWidth(55)
        self.edit_target_raw.textChanged.connect(self.refresh)
        row2.addWidget(self.edit_target_raw)
        self._target_ctrls = [self.lbl_target_z, self.edit_target_z,
                             self.lbl_target_raw, self.edit_target_raw]

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

    def switch_score_mode(self, full: bool):
        """切换客观分/满分卷模式"""
        self.dm.use_full_score = full
        self.btn_obj.setChecked(not full)
        self.btn_full.setChecked(full)
        if self._on_mode_change:
            self._on_mode_change()
        self.refresh()

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

    def _get_scores(self, students, use_zscore: bool = True):
        """获取最近一次考试成绩列表 [(name, score), ...]
        use_zscore=True 时返回标准分，False 时返回原始分
        """
        if use_zscore:
            zdata = self.dm.get_zscores(self.dm.current_class, self.dm.use_full_score)
            return [(name, z_list[-1]) for name, z_list in zdata]
        
        data = []
        for s in students:
            arr = s.scores if s.scores else s.scores_full
            if not arr:
                continue
            try:
                score = float(arr[-1][1])
                data.append((s.name, score))
            except (ValueError, IndexError, TypeError):
                continue
        return data

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

        scores = []
        for s in students:
            arr = s.scores if s.scores else s.scores_full
            if exam_idx < len(arr):
                try:
                    scores.append(float(arr[exam_idx][1]))
                except (ValueError, IndexError, TypeError):
                    pass

        if not scores:
            self._show_empty("无成绩数据")
            return

        ax = self.fig.add_subplot(111)

        # 原始分 → 比例分分段
        full_marks = 100 if self.dm.use_full_score else 40
        props = [sc / full_marks for sc in scores]

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

        mode_name = "满分卷" if self.dm.use_full_score else "客观分"
        exam_date = self.dm.dates[exam_idx] if exam_idx < len(self.dm.dates) else "未知"
        ax.set_ylabel("人数", fontsize=12)
        ax.set_xlabel("比例分段", fontsize=12)
        ax.set_title(f"成绩分布 ({mode_name}, {exam_date}, n={len(props)})", fontsize=14, fontweight="bold")
        ax.set_ylim(0, max(max(counts) * 1.2, 10))

        self._hover_dates = self.dm.dates
        self.status_label.setText(
            f"日期: {exam_date}  |  平均分: {sum(scores)/len(scores):.1f}  |  "
            f"最高分: {max(scores):.1f}  |  最低分: {min(scores):.1f}  |  "
            f"满分卷: {'是' if self.dm.use_full_score else '否'}"
        )

    def _draw_personal(self, students):
        """个人成绩趋势 — 标准分(左轴) + 原始分(右轴) 双纵轴"""
        name = self.combo_student.currentText()
        if not name:
            self._show_empty("请从下拉框选择学生")
            return

        # Z 分
        zdata = self.dm.get_zscores(self.dm.current_class, self.dm.use_full_score)
        student_z = next(((n, z) for n, z in zdata if n == name), None)
        if student_z is None:
            self._show_empty(f"未找到学生: {name}")
            return
        _, z_scores = student_z

        # 原始分
        full_marks = 100 if self.dm.use_full_score else 40
        raw_scores = []
        for s in students:
            if s.name == name:
                for item in (s.scores if s.scores else s.scores_full):
                    try:
                        raw_scores.append(float(item[1]))
                    except (ValueError, TypeError):
                        raw_scores.append(0.0)
                break

        if not z_scores and not raw_scores:
            self._show_empty(f"{name} 无成绩数据")
            return

        dates = self.dm.dates[:max(len(z_scores), len(raw_scores))]

        is_last7 = self.chk_last7.isChecked()
        if is_last7:
            n = min(7, len(z_scores))
            dates = dates[-n:]
            z_scores = z_scores[-n:]
            raw_scores = raw_scores[-n:]

        n_pts = len(z_scores)
        step = max(1, n_pts // 8)
        tick_pos = list(range(0, n_pts, step))
        x = list(range(n_pts))

        # ===== 上图：Z 标准分 =====
        ax1 = self.fig.add_subplot(211)

        ax1.plot(x, z_scores, marker="o", linewidth=2.5,
                 color="#1EAEE7", label="标准分 Z", markersize=7, zorder=3)

        ax1.axhline(y=0, color="#999", linestyle="-", linewidth=0.8, alpha=0.5)
        lim_z = max(abs(min(z_scores)), abs(max(z_scores))) * 1.25 + 0.3
        ax1.set_ylim(-lim_z, lim_z)
        ax1.set_ylabel("标准分 (Z)", fontsize=11)
        title = f"{name} — 标准分 (Z)" + (" (最近7次)" if is_last7 else f" (共{n_pts}次)")
        ax1.set_title(title, fontsize=13, fontweight="bold")
        ax1.legend(fontsize=9, loc="upper left")
        ax1.grid(True, linestyle="--", alpha=0.4)
        ax1.set_xticks(tick_pos)
        ax1.set_xticklabels([])  # 上图的 x 标签隐藏

        if is_last7:
            for xi, sc in zip(x, z_scores):
                ax1.text(xi, sc + 0.12, f"{sc:.2f}", ha="center", fontsize=8, color="#1EAEE7")

        # ===== 下图：原始分 =====
        ax2 = self.fig.add_subplot(212)

        ax2.plot(x, raw_scores, marker="s", linewidth=2.5,
                 color="#8e44ad", markersize=7, zorder=3)

        # 班级平均分
        class_avg = []
        for exam_i in range(n_pts):
            vals = []
            for s in students:
                arr = s.scores if s.scores else s.scores_full
                if exam_i < len(arr):
                    try:
                        vals.append(float(arr[exam_i][1]))
                    except (ValueError, TypeError):
                        pass
            class_avg.append(sum(vals) / len(vals) if vals else 0)
        ax2.plot(x, class_avg, color="#e74c3c", linestyle="--", linewidth=2.2,
                 label="班级平均分", zorder=4, alpha=0.9)

        r_min, r_max = min(raw_scores), max(raw_scores)
        r_pad = max((r_max - r_min) * 0.3, 3)
        ax2.set_ylim(r_min - r_pad, r_max + r_pad)
        mode_name = "仅客观分" if not self.dm.use_full_score else "整卷分"
        ax2.set_ylabel(f"原始分 (满分{full_marks})", fontsize=11)
        title2 = f"{name} — {mode_name}" + (" (最近7次)" if is_last7 else f" (共{n_pts}次)")
        ax2.set_title(title2, fontsize=13, fontweight="bold")
        ax2.legend(fontsize=9, loc="upper left")
        ax2.grid(True, linestyle="--", alpha=0.4)
        ax2.set_xticks(tick_pos)
        ax2.set_xticklabels([dates[i] for i in tick_pos], rotation=45, ha="right")
        ax2.set_xlabel("考试日期" if is_last7 else "考试次数", fontsize=11)

        self._hover_dates = dates
        self._hover_raw = raw_scores
        self.status_label.setText(
            f"{name} | {'最近7次' if is_last7 else f'共{n_pts}次'} | "
            f"均分 {sum(raw_scores)/n_pts:.1f} | "
            f"最高 {max(raw_scores):.1f} | 最低 {min(raw_scores):.1f}"
        )

    def _draw_latest(self, students):
        """最近一次考试柱状图 — Z分(上) + 原始分(下)"""
        data_z = self._get_scores(students)
        if not data_z:
            self._show_empty("无成绩数据")
            return

        # 也获取原始分
        data_raw = []
        for s in students:
            arr = s.scores if s.scores else s.scores_full
            if arr:
                try:
                    data_raw.append((s.name, float(arr[-1][1])))
                except (ValueError, TypeError):
                    pass

        data_z.sort(key=lambda x: x[1], reverse=True)
        # 原始分按 Z 分同名排序
        z_dict = dict(data_z)
        data_raw.sort(key=lambda x: z_dict.get(x[0], 0), reverse=True)

        page_data_z = self._get_paged_data(data_z)
        page_data_raw = self._get_paged_data(data_raw)

        if not page_data_z:
            self._group_offset = 0
            page_data_z = self._get_paged_data(data_z)
            page_data_raw = self._get_paged_data(data_raw)

        names = [d[0] for d in page_data_z]
        scores_z = [d[1] for d in page_data_z]
        scores_raw = [d[1] for d in page_data_raw]

        total = len(data_z)
        start = self._group_offset + 1
        end = min(self._group_offset + len(page_data_z), total)

        # ===== 上图：Z 标准分 =====
        ax1 = self.fig.add_subplot(211)
        colors_z = ["#1abc9c" if s >= 0 else "#f1c40f" if s >= -0.5 else "#e74c3c"
                    for s in scores_z]
        bars = ax1.barh(range(len(names)), scores_z, color=colors_z, height=0.6)
        ax1.set_yticks(range(len(names)))
        ax1.set_yticklabels(names, fontsize=9)
        ax1.invert_yaxis()
        lim_z = max(abs(min(scores_z)), abs(max(scores_z))) * 1.25 + 0.3
        ax1.set_xlim(-lim_z, lim_z)
        ax1.axvline(x=0, color="#999", linewidth=0.8, alpha=0.5)
        ax1.set_xlabel("标准分 (Z)", fontsize=11)
        ax1.set_title(f"最近一次考试 (第 {start}-{end} / {total} 名)", fontsize=13, fontweight="bold")
        for i, sc in enumerate(scores_z):
            ax1.text(sc + 0.02, i, f"{sc:.2f}", va="center", fontsize=8)

        # ===== 下图：原始分 =====
        ax2 = self.fig.add_subplot(212)
        colors_raw = ["#3498db" for _ in scores_raw]
        bars2 = ax2.barh(range(len(names)), scores_raw, color=colors_raw, height=0.6)
        ax2.set_yticks(range(len(names)))
        ax2.set_yticklabels(names, fontsize=9)
        ax2.invert_yaxis()
        full_marks = 100 if self.dm.use_full_score else 40
        ax2.set_xlim(0, full_marks * 1.1)
        ax2.set_xlabel(f"原始分 (满分{full_marks})", fontsize=11)
        # 标注（全班的实际均分，而非仅当前页面）
        class_avg = sum(v for _, v in data_raw) / len(data_raw) if data_raw else 0
        ax2.axvline(x=class_avg, color="#e74c3c", linewidth=1.5, linestyle="--",
                    alpha=0.7)
        ax2.text(class_avg + 0.5, len(names) - 0.5, f"全班均{class_avg:.1f}",
                 color="#e74c3c", fontsize=9, fontweight="bold")
        for i, sc in enumerate(scores_raw):
            ax2.text(sc + 0.3, i, f"{sc:.1f}", va="center", fontsize=8)

        mode_name = "满分卷" if self.dm.use_full_score else "客观分"
        self.status_label.setText(
            f"共 {total} 人 | 显示第 {start}-{end} 名 | {mode_name}"
        )

    def _draw_last7(self, students):
        """进退步榜：最近 N 次考试 Z 分变化排名"""
        zdata = self.dm.get_zscores(self.dm.current_class, self.dm.use_full_score)
        if not zdata:
            self._show_empty("无标准分数据")
            return

        n = min(7, len(self.dm.dates))
        dates = self.dm.dates[-n:]

        changes = []
        for name, z_list in zdata:
            seg = z_list[-n:]
            if len(seg) >= 2:
                k = len(seg)
                mx = (k - 1) / 2
                my = sum(seg) / k
                num = sum((i - mx) * (seg[i] - my) for i in range(k))
                den = sum((i - mx) ** 2 for i in range(k))
                slope = num / den if den != 0 else 0
                diff = slope * (k - 1)  # 趋势线上首尾差值
                trend_start = my - slope * mx
                trend_end = my + slope * mx
                changes.append((name, diff, trend_start, trend_end))
            else:
                changes.append((name, 0.0, seg[0] if seg else 0.0,
                                seg[-1] if seg else 0.0))

        changes.sort(key=lambda x: x[1], reverse=True)

        if not changes:
            self._show_empty("数据不足")
            return

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
        bars = ax.barh(range(len(names)), diffs, color=colors, height=0.7, edgecolor="white")

        for i, (bar, d, fv, lv) in enumerate(zip(bars, diffs, firsts, lasts)):
            sign = "+" if d >= 0 else ""
            text = f"{sign}{d:.2f}  ({fv:.2f} → {lv:.2f})"
            offset = max(abs(d) * 0.02, 0.03)
            x_pos = d + offset if d >= 0 else d - offset
            ha = "left" if d >= 0 else "right"
            ax.text(x_pos, i, text, va="center", ha=ha, fontsize=10)

        base = max(abs(min(diffs)), abs(max(diffs)), 0.2)
        ax.set_xlim(-base * 1.3 - 0.5, base * 1.3 + 0.5)
        ax.axvline(x=0, color="#999", linewidth=0.8, alpha=0.5)
        ax.spines["right"].set_visible(False)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel("Z 分变化", fontsize=12)
        mode = "满分卷" if self.dm.use_full_score else "客观分"
        ax.set_title(f"最近 {n} 次考试进退步榜 ({dates[0]} → {dates[-1]}) "
                     f"第 {start+1}-{end}/{total} 名 | {mode}",
                     fontsize=13, fontweight="bold")

        up = sum(1 for d in diffs if d >= 0)
        down = len(diffs) - up
        self._hover_dates = []
        self.status_label.setText(
            f"最近{n}次 | 进步 {up} 人 | 退步 {down} 人 | "
            f"最大进步 {max(diffs):.2f} | 最大退步 {min(diffs):.2f} | {mode}"
        )

    def _draw_target(self, students):
        """目标分对比 — Z分差距 + 原始分差距，红线标记目标"""
        full_marks = 100 if self.dm.use_full_score else 40

        # Z 分目标
        try:
            target_z = float(self.edit_target_z.text())
        except ValueError:
            target_z = 0
        try:
            target_raw = float(self.edit_target_raw.text())
        except ValueError:
            target_raw = 0

        # Z 分数据
        zdata = self.dm.get_zscores(self.dm.current_class, self.dm.use_full_score)
        z_scores = {}
        for name, z_list in zdata:
            if z_list:
                z_scores[name] = z_list[-1]

        # 原始分数据
        raw_scores = {}
        for s in students:
            arr = s.scores if s.scores else s.scores_full
            if arr:
                try:
                    raw_scores[s.name] = float(arr[-1][1])
                except (ValueError, TypeError):
                    pass

        # 合并
        data_z = []
        data_raw = []
        for name in z_scores:
            if name in z_scores and name in raw_scores:
                data_z.append((name, z_scores[name], z_scores[name] - target_z))
                data_raw.append((name, raw_scores[name], raw_scores[name] - target_raw))

        if not data_z:
            self._show_empty("无成绩数据")
            return

        data_z.sort(key=lambda x: x[2], reverse=True)
        # 原始分同步排序
        z_names = [d[0] for d in data_z]
        data_raw.sort(key=lambda x: z_names.index(x[0]) if x[0] in z_names else 999)

        page_z = self._get_paged_data(data_z)
        page_raw = self._get_paged_data(data_raw)

        if not page_z:
            self._group_offset = 0
            page_z = self._get_paged_data(data_z)
            page_raw = self._get_paged_data(data_raw)

        names = [d[0] for d in page_z]
        diffs_z = [d[2] for d in page_z]
        diffs_raw = [d[2] for d in page_raw]

        total = len(data_z)
        start = self._group_offset + 1
        end = min(self._group_offset + len(page_z), total)

        # ===== 上图：Z 分差距 + 目标红线 =====
        ax1 = self.fig.add_subplot(211)
        colors_z = ["#2ecc71" if d >= 0 else "#e74c3c" for d in diffs_z]
        ax1.barh(range(len(names)), diffs_z, color=colors_z, height=0.6)
        ax1.set_yticks(range(len(names)))
        ax1.set_yticklabels(names, fontsize=9)
        ax1.invert_yaxis()
        ax1.axvline(x=0, color="#e74c3c", linewidth=1.5, alpha=0.8, label=f"目标Z={target_z:.2f}")
        ax1.legend(fontsize=11, loc="lower right")
        ax1.set_xlabel(f"Z 分差距 (目标={target_z:.2f})", fontsize=11)
        ax1.set_title(f"目标分对比 (第 {start}-{end} / {total} 名)", fontsize=13, fontweight="bold")
        for i, d in enumerate(diffs_z):
            sign = "+" if d >= 0 else ""
            ax1.text(d + 0.02, i, f"{sign}{d:.2f}", va="center", fontsize=8)

        # ===== 下图：原始分差距 + 目标红线 =====
        ax2 = self.fig.add_subplot(212)
        colors_raw = ["#2ecc71" if d >= 0 else "#e74c3c" for d in diffs_raw]
        ax2.barh(range(len(names)), diffs_raw, color=colors_raw, height=0.6)
        ax2.set_yticks(range(len(names)))
        ax2.set_yticklabels(names, fontsize=9)
        ax2.invert_yaxis()
        ax2.axvline(x=0, color="#e74c3c", linewidth=1.5, alpha=0.8,
                    label=f"目标分={target_raw:.1f}")
        ax2.legend(fontsize=11, loc="lower right")
        ax2.set_xlabel(f"原始分差距 (目标={target_raw:.1f}, 满分{full_marks})", fontsize=11)
        for i, d in enumerate(diffs_raw):
            sign = "+" if d >= 0 else ""
            ax2.text(d + 0.3, i, f"{sign}{d:.1f}", va="center", fontsize=8)

        above_z = sum(1 for d in diffs_z if d >= 0)
        mode = "满分卷" if self.dm.use_full_score else "客观分"
        self.status_label.setText(
            f"目标Z={target_z:.2f}|达标{above_z}/{len(diffs_z)} | "
            f"目标分={target_raw:.1f} | {mode}"
        )

    # ------------------------------------------------------------------
    # 分页
    # ------------------------------------------------------------------
    def prev_group(self):
        students = self.dm.current_students
        data = self._get_scores(students)
        if not data:
            return
        total = len(data)
        self._group_offset = (self._group_offset - self._display_count) % total
        self.refresh()

    def next_group(self):
        students = self.dm.current_students
        data = self._get_scores(students)
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
