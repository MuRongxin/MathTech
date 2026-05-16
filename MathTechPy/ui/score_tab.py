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
    QPushButton, QSpinBox, QLineEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core.data_manager import DataManager


class ScoreTab(QWidget):
    MODE_DISTRIBUTION = "📊 成绩分布"
    MODE_PERSONAL = "👤 个人趋势"
    MODE_LATEST = "📋 最近一次"
    MODE_LAST7 = "📉 最近7次"
    MODE_TARGET = "🎯 目标分对比"

    def __init__(self, dm: DataManager):
        super().__init__()
        self.dm = dm
        self._current_mode = self.MODE_DISTRIBUTION
        self._display_count = 15
        self._group_offset = 0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ---------- 工具栏 ----------
        toolbar = QHBoxLayout()

        toolbar.addWidget(QLabel("图表模式:"))
        self.combo_mode = QComboBox()
        self.combo_mode.addItems([
            self.MODE_DISTRIBUTION,
            self.MODE_PERSONAL,
            self.MODE_LATEST,
            self.MODE_LAST7,
            self.MODE_TARGET,
        ])
        self.combo_mode.currentTextChanged.connect(self.on_mode_changed)
        toolbar.addWidget(self.combo_mode)

        toolbar.addSpacing(20)

        # 成绩模式切换
        self.btn_obj = QPushButton("客观分")
        self.btn_obj.setCheckable(True)
        self.btn_obj.setChecked(True)
        self.btn_obj.clicked.connect(lambda: self.switch_score_mode(False))
        toolbar.addWidget(self.btn_obj)

        self.btn_full = QPushButton("满分卷")
        self.btn_full.setCheckable(True)
        self.btn_full.clicked.connect(lambda: self.switch_score_mode(True))
        toolbar.addWidget(self.btn_full)

        toolbar.addSpacing(20)

        # 学生选择（个人模式用）
        self.lbl_student = QLabel("学生:")
        self.combo_student = QComboBox()
        self.combo_student.setMinimumWidth(150)
        self.combo_student.currentIndexChanged.connect(self.refresh)
        toolbar.addWidget(self.lbl_student)
        toolbar.addWidget(self.combo_student)

        # 最近7次开关（个人模式用）
        self.chk_last7 = QPushButton("📅 只看最近7次")
        self.chk_last7.setCheckable(True)
        self.chk_last7.setChecked(False)
        self.chk_last7.clicked.connect(self.refresh)
        toolbar.addWidget(self.chk_last7)

        # 目标分输入（目标分对比用）
        self.lbl_target = QLabel("目标分:")
        self.edit_target = QLineEdit("0")
        self.edit_target.setMaximumWidth(80)
        self.edit_target.textChanged.connect(self.refresh)
        toolbar.addWidget(self.lbl_target)
        toolbar.addWidget(self.edit_target)

        toolbar.addSpacing(20)

        # 显示人数（柱状图用）
        self.lbl_count = QLabel("显示人数:")
        self.spin_count = QSpinBox()
        self.spin_count.setRange(5, 100)
        self.spin_count.setValue(15)
        self.spin_count.valueChanged.connect(self.on_count_changed)
        toolbar.addWidget(self.lbl_count)
        toolbar.addWidget(self.spin_count)

        # 翻页按钮
        self.btn_prev = QPushButton("◀ 上一组")
        self.btn_prev.clicked.connect(self.prev_group)
        toolbar.addWidget(self.btn_prev)

        self.btn_next = QPushButton("下一组 ▶")
        self.btn_next.clicked.connect(self.next_group)
        toolbar.addWidget(self.btn_next)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # ---------- 图表区 ----------
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvas(self.fig)
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
        self.refresh()

    def _update_toolbar_visibility(self):
        """根据模式显示/隐藏控件"""
        is_personal = self._current_mode == self.MODE_PERSONAL
        is_target = self._current_mode == self.MODE_TARGET
        is_paged = self._current_mode in (self.MODE_LATEST, self.MODE_TARGET)
        is_dist = self._current_mode == self.MODE_DISTRIBUTION
        is_last7 = self._current_mode == self.MODE_LAST7

        self.lbl_student.setVisible(is_personal)
        self.combo_student.setVisible(is_personal)
        self.chk_last7.setVisible(is_personal)

        self.lbl_target.setVisible(is_target)
        self.edit_target.setVisible(is_target)

        self.lbl_count.setVisible(is_paged)
        self.spin_count.setVisible(is_paged)
        self.btn_prev.setVisible(is_paged)
        self.btn_next.setVisible(is_paged)

    def refresh(self):
        """刷新图表"""
        students = self.dm.current_students
        if not students:
            self._show_empty("当前班级没有学生数据")
            return

        # 只在个人/目标分模式需要时更新学生下拉框
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

        self.fig.tight_layout()
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
        scores = [sc for _, sc in self._get_scores(students)]

        if not scores:
            self._show_empty("无成绩数据")
            return

        ax = self.fig.add_subplot(111)

        # 原始分 → 比例分分段
        full_marks = 100 if self.dm.use_full_score else 40
        props = [sc / full_marks for _, sc in scores]

        bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        labels = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
        counts = [0] * (len(bins) - 1)
        for p in props:
            for i in range(len(bins) - 1):
                if bins[i] <= p <= bins[i + 1]:
                    counts[i] += 1
                    break

        colors = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c"]
        bars = ax.bar(labels, counts, color=colors, edgecolor="white", width=0.6)

        for bar, cnt in zip(bars, counts):
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, height + 0.5,
                        str(cnt), ha="center", va="bottom", fontsize=12, fontweight="bold")

        mode_name = "满分卷" if self.dm.use_full_score else "客观分"
        ax.set_ylabel("人数", fontsize=12)
        ax.set_xlabel("比例分段", fontsize=12)
        ax.set_title(f"成绩分布 ({mode_name}, n={len(props)})", fontsize=14, fontweight="bold")
        ax.set_ylim(0, max(max(counts) * 1.2, 10))

        self.status_label.setText(
            f"平均Z: {sum(scores)/len(scores):.2f}  |  "
            f"最高Z: {max(scores):.2f}  |  最低Z: {min(scores):.2f}  |  "
            f"满分卷: {'是' if self.dm.use_full_score else '否'}"
        )

    def _draw_personal(self, students):
        """个人成绩趋势折线图（标准分）"""
        name = self.combo_student.currentText()
        if not name:
            self._show_empty("请从下拉框选择学生")
            return

        # 从标准分数据中找到该学生
        zdata = self.dm.get_zscores(self.dm.current_class, self.dm.use_full_score)
        student_z = next(((n, z) for n, z in zdata if n == name), None)
        if student_z is None:
            self._show_empty(f"未找到学生: {name}")
            return

        _, z_scores = student_z
        if not z_scores:
            self._show_empty(f"{name} 无成绩数据")
            return

        dates = self.dm.dates[:len(z_scores)]

        # 最近7次过滤
        is_last7 = self.chk_last7.isChecked()
        if is_last7:
            n = min(7, len(z_scores))
            dates = dates[-n:]
            z_scores = z_scores[-n:]

        ax = self.fig.add_subplot(111)

        step = max(1, len(dates) // 8)
        tick_pos = list(range(0, len(dates), step))

        x = list(range(len(z_scores)))
        ax.plot(x, z_scores, marker="o", linewidth=2.5,
                color="#1EAEE7", label=name, markersize=6)

        avg = sum(z_scores) / len(z_scores) if z_scores else 0
        ax.axhline(y=avg, color="#e74c3c", linestyle="--",
                   label=f"平均Z {avg:.2f}")
        ax.axhline(y=0, color="#999", linestyle="-", linewidth=0.8, alpha=0.5)

        # 最近7次时标注每次分数
        if is_last7:
            for xi, sc in zip(x, z_scores):
                ax.text(xi, sc + 0.15, f"{sc:.2f}", ha="center", fontsize=9)

        ax.set_ylim(-3, 4)
        ax.set_ylabel("标准分 (Z)", fontsize=12)
        ax.set_xlabel("考试日期" if is_last7 else "考试次数", fontsize=12)
        title = f"{name} 的最近7次成绩" if is_last7 else f"{name} 的成绩趋势 (共{len(z_scores)}次)"
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.legend()
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_xticks(tick_pos)
        ax.set_xticklabels([dates[i] for i in tick_pos], rotation=45, ha="right")

        self.status_label.setText(
            f"{name} | {'最近7次' if is_last7 else f'共{len(z_scores)}次'} | "
            f"平均Z: {avg:.2f} | 最高Z: {max(z_scores):.2f} | 最低Z: {min(z_scores):.2f}"
        )

    def _draw_latest(self, students):
        """最近一次考试柱状图"""
        data = self._get_scores(students)
        if not data:
            self._show_empty("无成绩数据")
            return

        data.sort(key=lambda x: x[1], reverse=True)
        page_data = self._get_paged_data(data)

        if not page_data:
            self._group_offset = 0
            page_data = self._get_paged_data(data)

        ax = self.fig.add_subplot(111)

        names = [d[0] for d in page_data]
        scores = [d[1] for d in page_data]

        colors = ["#1abc9c" if s >= 0 else "#f1c40f" if s >= -0.5 else "#e74c3c"
                  for s in scores]
        bars = ax.barh(range(len(names)), scores, color=colors, height=0.6)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlim(-3, 4)
        ax.axvline(x=0, color="#999", linewidth=0.8, alpha=0.5)
        ax.set_xlabel("分数", fontsize=12)
        total = len(data)
        start = self._group_offset + 1
        end = min(self._group_offset + len(page_data), total)
        ax.set_title(f"最近一次考试成绩 (第 {start}-{end} / {total} 名)",
                     fontsize=14, fontweight="bold")

        for i, (bar, sc) in enumerate(zip(bars, scores)):
            ax.text(sc + 0.02, i, f"{sc:.2f}", va="center", fontsize=8)

        self.status_label.setText(
            f"共 {total} 人 | 显示第 {start}-{end} 名 | "
            f"满分卷: {'是' if self.dm.use_full_score else '否'}"
        )

    def _draw_last7(self, students):
        """最近7次考试班级平均分趋势（标准分）"""
        if not self.dm.dates:
            self._show_empty("无日期数据")
            return

        zdata = self.dm.get_zscores(self.dm.current_class, self.dm.use_full_score)
        if not zdata:
            self._show_empty("无标准分数据")
            return

        n = min(7, len(self.dm.dates))
        idx_start = len(self.dm.dates) - n
        dates = self.dm.dates[idx_start:]

        avgs = []
        for exam_i in range(idx_start, len(self.dm.dates)):
            vals = [z[exam_i] for _, z in zdata if exam_i < len(z)]
            avgs.append(round(sum(vals) / len(vals), 2) if vals else 0.0)

        ax = self.fig.add_subplot(111)
        x = list(range(len(avgs)))
        ax.plot(x, avgs, marker="o", linewidth=2.5, color="#9b59b6", markersize=8)

        for xi, (d, v) in enumerate(zip(dates, avgs)):
            ax.text(xi, v + 0.15, f"{v:.2f}", ha="center", fontsize=9)

        ax.set_ylim(-3, 4)
        ax.axhline(y=0, color="#999", linestyle="-", linewidth=0.8, alpha=0.5)
        ax.set_ylabel("班级平均标准分", fontsize=12)
        ax.set_xlabel("考试日期", fontsize=12)
        ax.set_title(f"最近 {n} 次考试班级平均分趋势", fontsize=14, fontweight="bold")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=30, ha="right")

        mode = "满分卷" if self.dm.use_full_score else "客观分"
        self.status_label.setText(
            f"最近{n}次平均Z: {sum(avgs)/len(avgs):.2f} | 模式: {mode}"
        )

    def _draw_target(self, students):
        """目标分对比"""
        try:
            target = float(self.edit_target.text())
        except ValueError:
            target = 0

        data = []
        for s in students:
            arr = s.scores if s.scores else s.scores_full
            if not arr:
                continue
            try:
                score = float(arr[-1][1])
                diff = score - target
                data.append((s.name, score, diff))
            except (ValueError, TypeError):
                continue

        if not data:
            self._show_empty("无成绩数据")
            return

        data.sort(key=lambda x: x[2], reverse=True)
        page_data = self._get_paged_data(data)

        if not page_data:
            self._group_offset = 0
            page_data = self._get_paged_data(data)

        ax = self.fig.add_subplot(111)

        names = [d[0] for d in page_data]
        diffs = [d[2] for d in page_data]

        colors = ["#2ecc71" if d >= 0 else "#e74c3c" for d in diffs]
        bars = ax.barh(range(len(names)), diffs, color=colors, height=0.6)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=9)
        ax.invert_yaxis()
        ax.axvline(x=0, color="#999", linewidth=0.8, alpha=0.5)
        ax.set_xlabel(f"与目标Z分 {target:.2f} 的差距", fontsize=12)
        total = len(data)
        start = self._group_offset + 1
        end = min(self._group_offset + len(page_data), total)
        ax.set_title(f"目标分对比 (第 {start}-{end} / {total} 名)",
                     fontsize=14, fontweight="bold")

        for i, (bar, d) in enumerate(zip(bars, diffs)):
            sign = "+" if d >= 0 else ""
            offset = 0.05 if d >= 0 else -0.05
            ha = "left" if d >= 0 else "right"
            ax.text(d + offset, i, f"{sign}{d:.2f}", va="center", ha=ha, fontsize=8)

        above = sum(1 for _, _, d in data if d >= 0)
        mode = "满分卷" if self.dm.use_full_score else "客观分"
        self.status_label.setText(
            f"目标Z分: {target:.2f} | 达标: {above}/{total} ({above/total*100:.1f}%) | 模式: {mode}"
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
