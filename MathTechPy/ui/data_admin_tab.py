"""小可爱数据维护 — 学生管理 + 成绩导入"""
import shutil, re
from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QFileDialog,
    QMessageBox, QComboBox, QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent

from core.data_manager import DataManager

DATA_DIR = Path(__file__).parent.parent / "data"


class DataAdminTab(QWidget):
    """学生管理 + 成绩导入"""

    def __init__(self, dm: DataManager):
        super().__init__()
        self.dm = dm
        self._current_class: int = 0
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        title = QLabel("📥 小可爱数据维护")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        # ── 班级选择 ──
        cls_row = QHBoxLayout()
        cls_row.addWidget(QLabel("当前班级:"))
        self.combo_class = QComboBox()
        self.combo_class.setMinimumWidth(150)
        self.combo_class.currentIndexChanged.connect(self._on_class_changed)
        cls_row.addWidget(self.combo_class)
        cls_row.addStretch()
        layout.addLayout(cls_row)

        # ── 学生管理 ──
        grp_stu = QGroupBox("👥 学生管理")
        stu_layout = QVBoxLayout(grp_stu)

        self.stu_table = QTableWidget(0, 3)
        self.stu_table.setHorizontalHeaderLabels(["学号", "姓名", ""])
        self.stu_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #ecf0f1; border-radius: 8px; }
            QHeaderView::section { background: #f8f9fa; padding: 6px; font-weight: bold; }
        """)
        self.stu_table.horizontalHeader().setStretchLastSection(True)
        self.stu_table.setColumnWidth(0, 120)
        self.stu_table.setColumnWidth(1, 200)
        stu_layout.addWidget(self.stu_table)

        add_row = QHBoxLayout()
        add_row.addWidget(QLabel("学号:"))
        self.edit_sid = QLineEdit()
        self.edit_sid.setMaximumWidth(100)
        add_row.addWidget(self.edit_sid)
        add_row.addWidget(QLabel("姓名:"))
        self.edit_sname = QLineEdit()
        self.edit_sname.setMaximumWidth(200)
        add_row.addWidget(self.edit_sname)
        self.btn_add_stu = QPushButton("＋ 添加")
        self.btn_add_stu.clicked.connect(self._add_student)
        add_row.addWidget(self.btn_add_stu)
        add_row.addStretch()
        stu_layout.addLayout(add_row)

        layout.addWidget(grp_stu)

        # ── 导入成绩 ──
        grp_score = QGroupBox("📥 导入考试数据")
        score_layout = QVBoxLayout(grp_score)

        self.import_drop = QLabel("📂 拖入 CSV/XLSX 文件 或 点击选择")
        self.import_drop.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.import_drop.setMinimumHeight(60)
        self.import_drop.setStyleSheet("""
            QLabel { border: 2px dashed #bdc3c7; border-radius: 12px;
                background: #fafafa; color: #95a5a6; font-size: 14px; }
        """)
        self.import_drop.mousePressEvent = self._on_import_click
        score_layout.addWidget(self.import_drop)
        self.setAcceptDrops(True)

        self.lbl_import_status = QLabel("")
        self.lbl_import_status.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        score_layout.addWidget(self.lbl_import_status)

        layout.addWidget(grp_score)

    # ------------------------------------------------------------------
    def refresh(self):
        self.combo_class.blockSignals(True)
        self.combo_class.clear()
        if self.dm.class_names:
            self.combo_class.addItems(self.dm.class_names)
            self.combo_class.setCurrentIndex(self._current_class)
        self.combo_class.blockSignals(False)
        self._load_students()

    def _on_class_changed(self, idx: int):
        if idx < 0:
            return
        self._current_class = idx
        self._load_students()

    # ------------------------------------------------------------------
    # 学生管理
    # ------------------------------------------------------------------
    def _load_students(self):
        self.stu_table.setRowCount(0)
        if not self.dm.students or self._current_class >= len(self.dm.students):
            return
        for i, s in enumerate(self.dm.students[self._current_class][0]):
            self.stu_table.insertRow(i)
            self.stu_table.setItem(i, 0, QTableWidgetItem(str(s.id)))
            self.stu_table.setItem(i, 1, QTableWidgetItem(s.name))
            btn = QPushButton("✕")
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("border: none; color: #bdc3c7; font-size: 14px;")
            btn.clicked.connect(lambda checked, r=i: self._delete_student(r))
            self.stu_table.setCellWidget(i, 2, btn)

    def _add_student(self):
        sid = self.edit_sid.text().strip()
        name = self.edit_sname.text().strip()
        if not name:
            return
        if not sid:
            sid = str(self.stu_table.rowCount() + 1)
        row = self.stu_table.rowCount()
        self.stu_table.insertRow(row)
        self.stu_table.setItem(row, 0, QTableWidgetItem(sid))
        self.stu_table.setItem(row, 1, QTableWidgetItem(name))
        btn = QPushButton("✕")
        btn.setFixedSize(28, 28)
        btn.setStyleSheet("border: none; color: #bdc3c7; font-size: 14px;")
        btn.clicked.connect(lambda checked, r=row: self._delete_student(r))
        self.stu_table.setCellWidget(row, 2, btn)
        self.edit_sid.clear()
        self.edit_sname.clear()
        self._save_students()

    def _delete_student(self, row: int):
        name = self.stu_table.item(row, 1).text() if self.stu_table.item(row, 1) else ""
        reply = QMessageBox.question(self, "确认删除",
                                     f"确定要删除学生「{name}」吗？")
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.stu_table.removeRow(row)
        for r in range(self.stu_table.rowCount()):
            btn = self.stu_table.cellWidget(r, 2)
            if btn:
                btn.clicked.disconnect()
                btn.clicked.connect(lambda checked, rr=int(r): self._delete_student(rr))
        self._save_students()

    def _save_students(self):
        if not self.dm.class_names:
            return
        ci = self._current_class
        # 重建学生列表
        from core.models import StudentData
        new_students = []
        for i in range(self.stu_table.rowCount()):
            sid = int(self.stu_table.item(i, 0).text()) if self.stu_table.item(i, 0) else i + 1
            name = self.stu_table.item(i, 1).text() if self.stu_table.item(i, 1) else ""
            if name:
                # 保留旧的 call_count
                old_stu = None
                for s in self.dm.students[ci][0]:
                    if s.name == name:
                        old_stu = s
                        break
                cc = old_stu.call_count if old_stu else 0
                new_students.append(StudentData(id=sid, name=name, call_count=cc))
        # 更新内存：保留旧学生的成绩数据，替换列表
        from core.models import StudentData
        old_score_maps = []
        for mode in range(3):
            maps = {}
            for s in self.dm.students[ci][mode]:
                maps[s.name] = (s.scores[:], s.scores_full[:], s.scores_sub[:], s.question_scores.copy())
            old_score_maps.append(maps)
        for mode in range(3):
            merged = []
            for s_new in new_students:
                old_data = old_score_maps[mode].get(s_new.name, ([], [], [], {}))
                copied = StudentData(s_new.id, s_new.name, s_new.call_count)
                copied.scores = old_data[0]
                copied.scores_full = old_data[1]
                copied.scores_sub = old_data[2]
                copied.question_scores = old_data[3]
                merged.append(copied)
            self.dm.students[ci][mode] = merged
        # 写回 XML
        xml_name = f"data_{self.dm.class_names[ci]}.xml"
        self.dm._save_xml(DATA_DIR / xml_name, new_students)

    # ------------------------------------------------------------------
    # 导入成绩
    # ------------------------------------------------------------------
    def _on_import_click(self, event):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "选择考试成绩文件", "",
            "表格文件 (*.csv *.xlsx);;所有文件 (*)")
        for p in paths:
            self._import_file(Path(p))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() in (".csv", ".xlsx"):
                self._import_file(path)

    def _import_file(self, path: Path):
        """复制文件到 question_scores/，解析文件名验证格式"""
        stem = path.stem
        parts = stem.split("_")
        if len(parts) < 5:
            QMessageBox.warning(self, "文件名格式错误",
                                f"文件名应为: quiz_YYYY_MM_DD_AXX.csv\n"
                                f"当前: {path.name}")
            return

        date_str = f"{parts[1]}/{parts[2]}/{parts[3]}"
        class_suffix = parts[4].replace("A", "")

        # 检查班级是否已配置
        known = [cn.replace("A", "") for cn in self.dm.class_names]
        if class_suffix not in known and self.dm.class_names:
            reply = QMessageBox.question(
                self, "班级不匹配",
                f"文件 {path.name} 的班级 A{class_suffix} 不在已配置班级中。\n"
                "仍要导入吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return

        # 复制
        dest = DATA_DIR / "question_scores" / path.name
        dest.parent.mkdir(exist_ok=True)
        shutil.copy2(path, dest)

        self.lbl_import_status.setText(
            f"已导入: {path.name} → {date_str} A{class_suffix}\n"
            "重启应用后生效。")
