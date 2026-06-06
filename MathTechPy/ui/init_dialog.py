"""初始化向导 — 首次启动时引导老师导入学生数据"""
import csv, re
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent

DATA_DIR = Path(__file__).parent.parent / "data"


class InitDialog(QDialog):
    """首次初始化：拖入成绩单 → 预览学生 → 确认生成配置"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("欢迎使用 MathTech — 初始化")
        self.setMinimumSize(600, 520)
        self._students: list[tuple[str, str]] = []  # [(student_id, name), ...]
        self._class_name: str = ""
        self._class_code: str = ""
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("欢迎使用 MathTech 🎓")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        subtitle = QLabel("请导入学生数据以开始使用。拖入成绩单 / 点名册文件（CSV 或 Excel），\n"
                          "或直接手动添加班级和学生。")
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 13px;")
        layout.addWidget(subtitle)

        # ── 拖放区域 ──
        self.drop_label = QLabel("📂 拖入文件到此 或 点击选择")
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setMinimumHeight(80)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7; border-radius: 12px;
                background: #fafafa; color: #95a5a6; font-size: 14px;
            }
        """)
        self.drop_label.mousePressEvent = self._on_click_drop
        layout.addWidget(self.drop_label)
        self.setAcceptDrops(True)

        # ── 班级信息 ──
        cls_row = QHBoxLayout()
        cls_row.addWidget(QLabel("班级名称:"))
        self.edit_class = QLineEdit()
        self.edit_class.setPlaceholderText("如 高三(1)班")
        self.edit_class.setStyleSheet("padding: 6px; border: 2px solid #dfe6e9; border-radius: 8px;")
        cls_row.addWidget(self.edit_class)
        cls_row.addWidget(QLabel("代号:"))
        self.edit_code = QLineEdit("A01")
        self.edit_code.setMaximumWidth(60)
        self.edit_code.setStyleSheet("padding: 6px; border: 2px solid #dfe6e9; border-radius: 8px;")
        cls_row.addWidget(self.edit_code)
        layout.addLayout(cls_row)

        # ── 学生表格 ──
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["学号", "姓名", ""])
        self.table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #ecf0f1; border-radius: 8px; }
            QHeaderView::section { background: #f8f9fa; padding: 6px; font-weight: bold; }
        """)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 150)
        layout.addWidget(self.table)

        # ── 操作按钮 ──
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("＋ 手动添加学生")
        self.btn_add.setStyleSheet("color: #1abc9c; border: none; font-size: 13px;")
        self.btn_add.clicked.connect(self._add_student)
        btn_row.addWidget(self.btn_add)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ── 底部 ──
        layout.addStretch()
        info = QLabel("将生成: config.xml, data_A01.xml, knowledge_pool.xml")
        info.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(info)

        self.btn_confirm = QPushButton("✓ 确认并开始使用")
        self.btn_confirm.setStyleSheet("""
            QPushButton { background: #1abc9c; color: white; border: none;
                border-radius: 10px; padding: 12px; font-size: 15px; font-weight: bold; }
            QPushButton:hover { background: #16a085; }
        """)
        self.btn_confirm.clicked.connect(self._on_confirm)
        layout.addWidget(self.btn_confirm)

    # ------------------------------------------------------------------
    def _on_click_drop(self, event):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择学生数据文件", "",
            "表格文件 (*.csv *.xlsx *.xls);;所有文件 (*)")
        if path:
            self._parse_file(Path(path))

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = Path(url.toLocalFile())
            if path.suffix.lower() in (".csv", ".xlsx", ".xls"):
                self._parse_file(path)
                break

    def _parse_file(self, path: Path):
        """解析文件，提取学生姓名和学号"""
        try:
            if path.suffix.lower() == ".csv":
                rows = self._read_csv(path)
            else:
                rows = self._read_xlsx(path)
        except Exception as e:
            QMessageBox.warning(self, "解析失败", f"无法读取文件: {e}")
            return

        if not rows or len(rows) < 1:
            QMessageBox.warning(self, "数据为空", "文件中未找到数据")
            return

        # 找表头行（同 data_manager 的逻辑）
        header_row = 0
        for ri, row in enumerate(rows[:5]):
            candidates = [str(c).strip() for c in row if c and str(c).strip()]
            if any(c in ("姓名", "学生姓名", "name", "Name") or
                   c in ("学号", "考号", "id", "ID", "student_id") or
                   any(ch.isdigit() for ch in c)
                   for c in candidates):
                if len(candidates) >= 2:
                    header_row = ri
                    break

        header = [str(c).strip() for c in rows[header_row]]
        # 找姓名列和学号列
        name_col = id_col = None
        for i, h in enumerate(header):
            if h in ("姓名", "学生姓名", "name", "Name"):
                name_col = i
            elif h in ("学号", "考号", "id", "ID", "student_id", "studentId"):
                id_col = i
        # 如果没找到姓名列，取第一列文本列
        if name_col is None:
            for i, h in enumerate(header):
                if h and not any(ch.isdigit() for ch in h[:3]):
                    name_col = i
                    break
        if name_col is None:
            name_col = 1 if len(header) > 1 else 0
        if id_col is None:
            id_col = 0 if 0 != name_col else (1 if len(header) > 1 else None)

        # 提取学生
        students = []
        for row in rows[header_row + 1:]:
            if not row or len(row) <= max(name_col, id_col or 0):
                continue
            name = str(row[name_col]).strip() if name_col < len(row) else ""
            if not name or name.lower() in ("姓名", "name", ""):
                continue
            sid = str(row[id_col]).strip() if id_col is not None and id_col < len(row) else ""
            if not sid:
                sid = str(len(students) + 1)
            students.append((sid, name))

        if not students:
            QMessageBox.warning(self, "未识别", "未能从文件中识别到学生姓名")
            return

        # 尝试从文件名提取班级代号
        stem = path.stem
        m = re.search(r'[Aa](\d+)', stem)
        if m:
            self.edit_code.setText(f"A{m.group(1).zfill(2)}")
        if not self.edit_class.text():
            self.edit_class.setText(f"班级{self.edit_code.text()}")

        self._students = students
        self._populate_table()

    def _read_csv(self, path: Path) -> list:
        with open(path, "r", encoding="utf-8-sig") as f:
            return list(csv.reader(f))

    def _read_xlsx(self, path: Path) -> list:
        import openpyxl
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        rows = [[cell for cell in row] for row in ws.iter_rows(values_only=True)]
        wb.close()
        return rows

    def _populate_table(self):
        self.table.setRowCount(0)
        for i, (sid, name) in enumerate(self._students):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(sid))
            self.table.setItem(i, 1, QTableWidgetItem(name))
            btn_del = QPushButton("✕")
            btn_del.setFixedSize(28, 28)
            btn_del.setStyleSheet("border: none; color: #bdc3c7; font-size: 14px;")
            btn_del.clicked.connect(lambda checked, r=i: self._delete_student(r))
            self.table.setCellWidget(i, 2, btn_del)

    def _add_student(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 1, QTableWidgetItem(""))
        btn_del = QPushButton("✕")
        btn_del.setFixedSize(28, 28)
        btn_del.setStyleSheet("border: none; color: #bdc3c7; font-size: 14px;")
        btn_del.clicked.connect(lambda checked, r=row: self._delete_student(r))
        self.table.setCellWidget(row, 2, btn_del)

    def _delete_student(self, row: int):
        self.table.removeRow(row)
        # 更新删除按钮引用
        for r in range(self.table.rowCount()):
            btn = self.table.cellWidget(r, 2)
            if btn:
                btn.clicked.disconnect()
                btn.clicked.connect(lambda checked, rr=r: self._delete_student(rr))

    # ------------------------------------------------------------------
    def _on_confirm(self):
        class_name = self.edit_class.text().strip()
        class_code = self.edit_code.text().strip()
        if not class_name:
            QMessageBox.warning(self, "缺少班级名", "请输入班级名称")
            return
        if not class_code:
            class_code = "A01"
            self.edit_code.setText(class_code)

        # 收集表格中的学生
        students = []
        for i in range(self.table.rowCount()):
            sid_item = self.table.item(i, 0)
            name_item = self.table.item(i, 1)
            sid = sid_item.text().strip() if sid_item else str(i + 1)
            name = name_item.text().strip() if name_item else ""
            if name:
                students.append((sid, name))
        if not students:
            QMessageBox.warning(self, "无学生", "请至少添加一名学生")
            return

        # 确保 data 目录存在
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # 生成班级 XML
        xml_path = DATA_DIR / f"data_{class_code}.xml"
        self._write_class_xml(xml_path, students)

        # 生成 config.xml（追加模式）
        config_path = DATA_DIR / "config.xml"
        self._write_config(config_path, xml_path.name)

        # 生成默认知识点池
        pool_path = DATA_DIR / "knowledge_pool.xml"
        if not pool_path.exists():
            from core.data_manager import DataManager
            dm = DataManager()
            dm._save_knowledge_pool(pool_path)

        # 确保 question_scores 目录存在
        (DATA_DIR / "question_scores").mkdir(exist_ok=True)

        QMessageBox.information(self, "初始化完成",
                                f"已创建 {class_name}({class_code})，共 {len(students)} 名学生。\n"
                                "现在可以导入考试数据了。")
        self.accept()

    def _write_class_xml(self, path: Path, students: list[tuple[str, str]]):
        import xml.etree.ElementTree as ET
        root = ET.Element("root")
        for i, (sid, name) in enumerate(students):
            stu = ET.SubElement(root, "student", {"id": sid})
            ET.SubElement(stu, "name").text = name
            ET.SubElement(stu, "callCount").text = "0"
        self._indent_xml(root)
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

    def _write_config(self, path: Path, xml_name: str):
        import xml.etree.ElementTree as ET
        if path.exists():
            tree = ET.parse(path)
            root = tree.getroot()
            # 检查是否已存在
            for elem in root.findall("classMembers"):
                if elem.text and elem.text.strip() == xml_name:
                    break
            else:
                ET.SubElement(root, "classMembers").text = xml_name
        else:
            root = ET.Element("config")
            ET.SubElement(root, "classMembers").text = xml_name
        self._indent_xml(root)
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

    def _indent_xml(self, elem, level=0):
        indent_str = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent_str + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent_str
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = "\n" + "  " * level
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent_str
