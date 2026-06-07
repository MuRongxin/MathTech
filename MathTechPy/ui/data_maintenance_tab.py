"""数据维护页面 — 考试知识点管理"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QFrame, QMessageBox,
    QInputDialog, QScrollArea, QButtonGroup, QSlider, QMenu,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QMimeData, QPropertyAnimation, QPoint, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QDrag, QDragEnterEvent, QDropEvent, QPainter, QPixmap

from core.data_manager import DataManager
from core.models import KnowledgeTopic, Question

MIME_CATEGORY = "application/x-category-drag"


class TagChip(QPushButton):
    """知识点标签：单击定位，双击移除"""

    def __init__(self, text: str, on_locate=None, on_remove=None, parent=None):
        super().__init__(text, parent)
        self._name = text.rsplit("(", 1)[0].strip() if "(" in text else text
        self._on_locate = on_locate
        self._on_remove = on_remove
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: #1abc9c; color: white; border: none;
                border-radius: 12px; padding: 4px 10px; font-size: 12px;
            }
            QPushButton:hover { background: #16a085; }
        """)
        self._double_clicked = False
        self.clicked.connect(self._on_click)

    def _on_click(self):
        if self._double_clicked:
            self._double_clicked = False
            return
        if self._on_locate:
            self._on_locate(self._name)

    def mouseDoubleClickEvent(self, event):
        self._double_clicked = True
        if self._on_remove:
            self._on_remove(self._name)


class TopicToggle(QPushButton):
    """知识点选择按钮（被 ToggleRow 内部使用）"""

    def __init__(self, category: str, name: str, parent=None):
        super().__init__(name, parent)
        self.category = category
        self.name = name
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(28)
        self._update_style()

    def _update_style(self):
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton {
                    background: #1abc9c; color: white; border: 2px solid #16a085;
                    border-radius: 12px; padding: 3px 10px; font-size: 12px;
                }
            """)
            self.setText(f"✓{self.name}")
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: white; color: #2c3e50; border: 2px solid #dfe6e9;
                    border-radius: 12px; padding: 3px 10px; font-size: 12px;
                }
                QPushButton:hover { border-color: #1abc9c; color: #1abc9c; }
            """)
            self.setText(self.name)


class ToggleRow(QWidget):
    """知识点按钮 + 权重滑动条"""

    def __init__(self, category: str, name: str, on_weight_change=None, on_menu=None, parent=None):
        super().__init__(parent)
        self.category = category
        self.name = name
        self._on_weight_change = on_weight_change
        self._on_menu = on_menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.toggle = TopicToggle(category, name)
        layout.addWidget(self.toggle)

        # 权重滑块
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(1, 100)
        self.slider.setValue(100)
        self.slider.setFixedWidth(50)
        self.slider.setVisible(False)
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7; border-radius: 3px;
                height: 4px; background: #ecf0f1;
            }
            QSlider::handle:horizontal {
                background: #1abc9c; border: none;
                width: 12px; height: 12px; margin: -5px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal { background: #1abc9c; border-radius: 3px; }
        """)
        layout.addWidget(self.slider)

        # 权重数字（双击可输入）
        self.weight_lbl = QLabel()
        self.weight_lbl.setFixedWidth(34)
        self.weight_lbl.setVisible(False)
        self.weight_lbl.setStyleSheet("color: #1abc9c; font-size: 11px; font-weight: bold;")
        self.weight_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weight_lbl.setCursor(Qt.CursorShape.IBeamCursor)
        self.weight_lbl.mouseDoubleClickEvent = self._on_lbl_dblclick
        layout.addWidget(self.weight_lbl)

        # 同步
        self.slider.valueChanged.connect(self._on_slider)
        self.toggle.toggled.connect(self._on_toggled)
        self._update_label()

    def _on_lbl_dblclick(self, event):
        pct = self.slider.value()
        self.weight_lbl.hide()
        edit = QLineEdit(str(pct))
        edit.setFixedSize(38, 20)
        edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #1abc9c; border-radius: 4px;
                padding: 0 2px; font-size: 11px; color: #2c3e50;
                background: white;
            }
        """)
        edit.selectAll()
        edit.setFocus()
        self.layout().replaceWidget(self.weight_lbl, edit)

        def finish():
            try:
                val = int(edit.text())
                val = max(1, min(100, val))
                self.slider.setValue(val)
            except ValueError:
                pass
            self.layout().replaceWidget(edit, self.weight_lbl)
            self.weight_lbl.show()
            edit.hide()
            edit.deleteLater()
            self._update_label()

        edit.editingFinished.connect(finish)
        # 失焦也触发
        def on_focus_out(e):
            if e.type() == e.Type.FocusOut:
                finish()
            return False
        edit.installEventFilter(self)
        self._active_edit = edit

    def _show_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #f8f9fa; border: 1px solid #dce3e8;
                border-radius: 10px; padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px; border-radius: 6px;
                color: #2c3e50;
            }
            QMenu::item:selected { background: #e0f0ea; color: #16a085; }
        """)
        act_rename = menu.addAction("✏️ 重命名知识点")
        act_delete = menu.addAction("🗑️ 删除知识点")
        act = menu.exec(self.mapToGlobal(pos))
        if act == act_rename and self._on_menu:
            self._on_menu("rename_topic", self.category, self.name)
        elif act == act_delete and self._on_menu:
            self._on_menu("delete_topic", self.category, self.name)

    def _on_slider(self, val: int):
        self._update_label()
        if self._on_weight_change:
            self._on_weight_change(self.name, self.get_weight())

    def _on_toggled(self, checked: bool):
        self.slider.setVisible(checked)
        self.weight_lbl.setVisible(checked)
        if not checked:
            self.slider.setValue(100)

    def _update_label(self):
        self.weight_lbl.setText(f"{self.slider.value():d}%")

    def set_checked(self, checked: bool):
        self.toggle.setChecked(checked)
        self.slider.setVisible(checked)
        self.weight_lbl.setVisible(checked)

    def is_checked(self) -> bool:
        return self.toggle.isChecked()

    def get_weight(self) -> float:
        return round(self.slider.value() / 100.0, 2)

    def set_weight(self, w: float):
        self.slider.blockSignals(True)
        self.slider.setValue(max(1, min(100, int(w * 100))))
        self.slider.blockSignals(False)
        self._update_label()


class CategoryGroup(QWidget):
    """一类知识点的折叠组（支持拖拽排序）"""

    def __init__(self, cat_name: str, topics: list[str], on_weight_change=None, on_menu=None, parent=None):
        super().__init__(parent)
        self.cat_name = cat_name
        self._drag_start = None
        self._on_menu = on_menu
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_menu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 标题行：拖动把手 + 展开按钮（用 QFrame 包住，方便抓取拖拽缩略图）
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("background: #f0f2f5; border-radius: 6px;")
        header_row = QHBoxLayout(self.header_frame)
        header_row.setSpacing(4)
        header_row.setContentsMargins(4, 2, 4, 2)

        # 拖动把手 ≡（视觉提示，整个 header 都可拖）
        self.grip = QLabel("≡")
        self.grip.setStyleSheet("""
            QLabel {
                color: #bdc3c7; font-size: 20px; font-weight: bold;
                padding: 0 4px; background: transparent;
            }
        """)
        self.grip.setFixedWidth(24)
        header_row.addWidget(self.grip)

        self.expand_btn = QPushButton()
        self.expand_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.expand_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none; text-align: left;
                padding: 4px 4px; font-size: 13px; font-weight: bold; color: #2c3e50;
            }
            QPushButton:hover { color: #1abc9c; }
        """)
        self.expand_btn.clicked.connect(self._toggle)
        self.expand_btn.setCursor(Qt.CursorShape.OpenHandCursor)
        header_row.addWidget(self.expand_btn, 1)

        layout.addWidget(self.header_frame)

        self.body = QWidget()
        self.body.setStyleSheet("background: transparent;")
        self.body.setVisible(False)
        from ui.random_tab import FlowLayout
        self.body_layout = FlowLayout(self.body, 6)
        self.body_layout.setContentsMargins(8, 2, 8, 2)
        self.toggles: list[ToggleRow] = []

        for t in topics:
            row = ToggleRow(cat_name, t, on_weight_change=on_weight_change, on_menu=on_menu)
            self.body_layout.addWidget(row)
            self.toggles.append(row)

        layout.addWidget(self.body)
        self._update_header()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start is None:
            return
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        delta = event.position().toPoint() - self._drag_start
        if delta.manhattanLength() < 6:
            return

        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(MIME_CATEGORY, self.cat_name.encode("utf-8"))
        mime.setText(self.cat_name)
        drag.setMimeData(mime)

        pixmap = self.header_frame.grab()
        pad = 14
        shadow_pm = QPixmap(pixmap.width() + 2 * pad, pixmap.height() + 2 * pad)
        shadow_pm.fill(Qt.GlobalColor.transparent)
        painter = QPainter(shadow_pm)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for i in range(10, 0, -1):
            alpha = int(35 * (11 - i) / 10)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, alpha))
            painter.drawRoundedRect(pad - i, pad - i + 3,
                                    pixmap.width() + 2 * i, pixmap.height() + 2 * i,
                                    8 + i, 8 + i)
        painter.setOpacity(0.92)
        painter.drawPixmap(pad, pad, pixmap)
        painter.end()

        scaled = shadow_pm.scaled(
            int(shadow_pm.width() * 1.05),
            int(shadow_pm.height() * 1.05),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        drag.setPixmap(scaled)
        drag.setHotSpot(QPoint(scaled.width() // 2, int(pad * 1.05) + pixmap.height() // 2))

        opacity = QGraphicsOpacityEffect(self.header_frame)
        opacity.setOpacity(0.35)
        self.header_frame.setGraphicsEffect(opacity)

        self._drag_start = None
        drag.exec(Qt.DropAction.MoveAction)

        old_effect = self.header_frame.graphicsEffect()
        if old_effect and isinstance(old_effect, QGraphicsOpacityEffect):
            fade_back = QPropertyAnimation(old_effect, b"opacity")
            fade_back.setDuration(200)
            fade_back.setStartValue(0.35)
            fade_back.setEndValue(1.0)
            fade_back.setEasingCurve(QEasingCurve.Type.OutCubic)
            fade_back.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

            def _cleanup():
                if self.header_frame.graphicsEffect() is old_effect:
                    self.header_frame.setGraphicsEffect(None)

            fade_back.finished.connect(_cleanup)
        else:
            self.header_frame.setGraphicsEffect(None)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat(MIME_CATEGORY):
            src = bytes(event.mimeData().data(MIME_CATEGORY)).decode("utf-8")
            if src != self.cat_name:
                self.setStyleSheet(self.styleSheet() + """
                    CategoryGroup { border: 2px dashed #1abc9c; border-radius: 6px; }
                """)
                event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")  # 清除非正常样式，但保留原始样式...

    def dropEvent(self, event):
        if event.mimeData().hasFormat(MIME_CATEGORY):
            src_name = bytes(event.mimeData().data(MIME_CATEGORY)).decode("utf-8")
            # 通过 DropContainer 处理
            container = self.parent()
            while container and not isinstance(container, DropContainer):
                container = container.parent()
            if isinstance(container, DropContainer) and container._drop_callback:
                # 找到在 container 中的目标索引
                children = [container.layout().itemAt(i).widget()
                            for i in range(container.layout().count())
                            if container.layout().itemAt(i).widget()]
                target_idx = len(children)
                for i, w in enumerate(children):
                    if w is self:
                        target_idx = i
                        break
                container._drop_callback(src_name, target_idx)
        event.acceptProposedAction()

    def _toggle(self):
        self.body.setVisible(not self.body.isVisible())
        self._update_header()

    def _show_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #f8f9fa; border: 1px solid #dce3e8;
                border-radius: 10px; padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px; border-radius: 6px;
                color: #2c3e50;
            }
            QMenu::item:selected { background: #e0f0ea; color: #16a085; }
            QMenu::separator { height: 1px; background: #dce3e8; margin: 4px 8px; }
        """)
        act_rename = menu.addAction("✏️ 重命名分类")
        act_delete = menu.addAction("🗑️ 删除分类")
        act = menu.exec(self.mapToGlobal(pos))
        if act == act_rename and self._on_menu:
            self._on_menu("rename_cat", self.cat_name)
        elif act == act_delete and self._on_menu:
            self._on_menu("delete_cat", self.cat_name)

    def expand(self):
        self.body.setVisible(True)
        self._update_header()

    def _update_header(self, selected_count: int = 0):
        arrow = "▼" if self.body.isVisible() else "▶"
        total = len(self.toggles)
        cnt_str = f"({selected_count}/{total})" if selected_count > 0 else f"({total})"
        self.expand_btn.setText(f"{arrow} {self.cat_name} {cnt_str}")

class DropContainer(QWidget):
    """可接收拖放的容器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._drop_callback = None

    def set_drop_callback(self, callback):
        self._drop_callback = callback

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasFormat(MIME_CATEGORY):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat(MIME_CATEGORY):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        if not self._drop_callback:
            return
        src_name = bytes(event.mimeData().data(MIME_CATEGORY)).decode("utf-8")
        # 计算目标位置
        children = [self.layout().itemAt(i).widget()
                    for i in range(self.layout().count())
                    if self.layout().itemAt(i).widget()]
        y = event.position().y()
        target_idx = len(children)
        for i, w in enumerate(children):
            if w and y < w.y() + w.height() / 2:
                target_idx = i
                break
        self._drop_callback(src_name, target_idx)


class DataMaintenanceTab(QWidget):
    """数据维护页 — 逐题知识点绑定"""

    TYPE_ABBREV = {"choice": "选", "multi_select": "多", "fill": "填", "answer": "解"}
    OBJ_COLOR = "#3498db"   # 客观题（选择、多选）
    SUB_COLOR = "#e67e22"   # 主观题（填空、解答）

    def __init__(self, dm: DataManager):
        super().__init__()
        self.dm = dm
        self._current_date = ""
        self._current_qid = ""                           # 当前选中的题号
        self._question_topics: dict[str, dict[str, float]] = {}  # {qid: {topic_name: weight}}
        self._question_buttons: list[QPushButton] = []

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._apply_search)

        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== 左侧：考试列表 =====
        left = QFrame()
        left.setFixedWidth(260)
        left.setStyleSheet("background: white; border-right: 1px solid #ecf0f1;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(12, 16, 12, 16)
        left_layout.setSpacing(8)

        lbl = QLabel("📅 考试列表")
        lbl.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #2c3e50;")
        left_layout.addWidget(lbl)

        self.search_exam = QLineEdit()
        self.search_exam.setPlaceholderText("🔍 搜索考试日期...")
        self.search_exam.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 6px 10px; font-size: 13px;
            }
            QLineEdit:focus { border-color: #1abc9c; }
        """)
        self.search_exam.textChanged.connect(lambda: self._search_timer.start(150))
        left_layout.addWidget(self.search_exam)

        self.exam_list = QListWidget()
        self.exam_list.setStyleSheet("""
            QListWidget { border: none; background: #fafafa; border-radius: 8px; }
            QListWidget::item {
                padding: 8px 12px; border-bottom: 1px solid #f0f0f0;
                color: #2c3e50; font-size: 13px;
            }
            QListWidget::item:selected {
                background: #1abc9c; color: white; border-radius: 6px;
                font-weight: bold;
            }
            QListWidget::item:selected:hover { background: #16a085; }
        """)
        self.exam_list.currentItemChanged.connect(self._on_exam_selected)
        left_layout.addWidget(self.exam_list)
        layout.addWidget(left)

        # ===== 右侧：编辑区 =====
        right = QFrame()
        right.setStyleSheet("background: #f5f6fa;")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(20, 16, 20, 16)
        right_layout.setSpacing(10)

        title = QLabel("🛠️ 数据维护")
        title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        right_layout.addWidget(title)

        self.lbl_current = QLabel("请从左侧选择考试日期")
        self.lbl_current.setFont(QFont("Microsoft YaHei", 12))
        self.lbl_current.setStyleSheet("color: #7f8c8d; padding: 2px 0;")
        right_layout.addWidget(self.lbl_current)

        # 编辑区（未选考试时禁用）
        self.edit_area = QWidget()
        self.edit_area.setEnabled(False)
        edit_layout = QVBoxLayout(self.edit_area)
        edit_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.setSpacing(10)

        # ---- 题目选择器（FlowLayout 按钮排） ----
        from ui.random_tab import FlowLayout
        qbtn_frame = QFrame()
        qbtn_frame.setStyleSheet("background: transparent;")
        self.qbtn_layout = FlowLayout(qbtn_frame, 4)
        self.qbtn_layout.setContentsMargins(0, 0, 0, 0)
        edit_layout.addWidget(qbtn_frame)

        # ---- 已选标签 ----
        tags_frame = QFrame()
        tags_frame.setStyleSheet("background: white; border-radius: 8px;")
        from ui.random_tab import FlowLayout
        self.tags_layout = FlowLayout(tags_frame, 8)
        self.tags_layout.setContentsMargins(12, 10, 12, 10)
        edit_layout.addWidget(tags_frame)

        # ---- 滚动区 ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(6)

        self.search_topic = QLineEdit()
        self.search_topic.setPlaceholderText("🔍 搜索知识点...")
        self.search_topic.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 8px 12px; font-size: 13px; background: white;
            }
            QLineEdit:focus { border-color: #1abc9c; }
        """)
        self.search_topic.textChanged.connect(self._on_topic_search)
        scroll_layout.addWidget(self.search_topic)

        # 可拖放容器
        self.cat_groups: list[CategoryGroup] = []
        self.cat_container = DropContainer()
        self.cat_container.set_drop_callback(self._on_drop)
        self.cat_container.setStyleSheet("background: transparent;")
        self.cat_layout = QVBoxLayout(self.cat_container)
        self.cat_layout.setContentsMargins(0, 0, 0, 0)
        self.cat_layout.setSpacing(2)

        self._build_cat_groups()

        scroll_layout.addWidget(self.cat_container)
        # ---- 右键菜单（空白区） ----
        scroll_content.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        scroll_content.customContextMenuRequested.connect(self._on_empty_menu)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        edit_layout.addWidget(scroll, 1)

        right_layout.addWidget(self.edit_area, 1)
        layout.addWidget(right, 1)

        self._refresh_exam_list()

    # ------------------------------------------------------------------
    # 拖拽排序
    # ------------------------------------------------------------------
    def _on_empty_menu(self, pos):
        sender_widget = self.sender()
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #f8f9fa; border: 1px solid #dce3e8;
                border-radius: 10px; padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px; border-radius: 6px;
                color: #2c3e50; text-align: left;
            }
            QMenu::item:selected { background: #e0f0ea; color: #16a085; }
        """)
        menu.addAction("＋ 新增知识点").triggered.connect(self._add_knowledge)
        menu.exec(sender_widget.mapToGlobal(pos))

    def _on_drop(self, src_name: str, target_idx: int):
        """处理拖拽放下"""
        self.dm.move_category(src_name, target_idx)
        self._rebuild_cat_groups()
        if self._current_date:
            self._sync_toggles()
            self._refresh_tags()

    # ------------------------------------------------------------------
    # 题目选择
    # ------------------------------------------------------------------
    def _on_question_selected(self, qid: str):
        if qid == self._current_qid:
            return
        self._save_current_question()
        self._current_qid = qid
        self._update_question_buttons()
        self._sync_toggles()
        self._refresh_tags()

    def _save_current_question(self):
        """保存当前题目的知识点到 _question_topics"""
        if not self._current_qid:
            return
        topics = {}
        for row in self._all_toggles():
            if row.is_checked():
                topics[row.name] = row.get_weight()
        if topics:
            self._question_topics[self._current_qid] = topics
        elif self._current_qid in self._question_topics:
            del self._question_topics[self._current_qid]
        self._auto_save()

    def _update_question_buttons(self):
        """刷新题目按钮的选中态和绑定标记"""
        bound_style = """
            QPushButton {
                background: white; color: #2c3e50;
                border: 2px solid #16a085; border-radius: 8px;
                padding: 4px 10px; font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { border-color: #0e6655; }
            QPushButton:checked { background: #1abc9c; color: white; border-color: #16a085; }
        """
        unbound_style_tpl = """
            QPushButton {{
                background: white; color: #95a5a6;
                border: 2px solid {border_color};
                border-radius: 8px;
                padding: 4px 10px; font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover {{ border-color: #1abc9c; color: #1abc9c; }}
            QPushButton:checked {{ background: #1abc9c; color: white; border-color: #16a085; }}
        """
        for btn in self._question_buttons:
            qid = btn.property("qid")
            btn.setChecked(qid == self._current_qid)
            count = len(self._question_topics.get(qid, {}))
            if count == 0:
                indicator = "-"
            elif count == 1:
                indicator = "❶"
            elif count == 2:
                indicator = "❷"
            else:
                indicator = str(count)
            qtype = btn.property("qtype")
            is_obj = qtype in ("choice", "multi_select")
            border_color = self.OBJ_COLOR if is_obj else self.SUB_COLOR
            abbrev = self.TYPE_ABBREV.get(qtype, "?")
            btn.setText(f"Q{qid} {abbrev} {indicator}")
            if count > 0:
                btn.setStyleSheet(bound_style)
            else:
                btn.setStyleSheet(unbound_style_tpl.format(border_color=border_color))

    # ------------------------------------------------------------------
    # 知识点切换
    # ------------------------------------------------------------------
    def _on_tag_locate(self, name: str):
        """单击标签 → 定位到知识点在列表中的位置"""
        for g in self.cat_groups:
            for row in g.toggles:
                if row.name == name:
                    g.expand()
                    # 滚动到可见（向上查找 QScrollArea）
                    p = self.cat_container.parent()
                    while p is not None and not isinstance(p, QScrollArea):
                        p = p.parent()
                    if p is not None:
                        p.ensureWidgetVisible(g, 50, 20)
                    # 高亮闪烁
                    row.toggle.setStyleSheet("""
                        QPushButton {
                            background: #f39c12; color: white; border: 2px solid #e67e22;
                            border-radius: 12px; padding: 3px 10px; font-size: 12px;
                        }
                    """)
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(600, lambda r=row: r.toggle._update_style())
                    return

    def _on_tag_remove(self, name: str):
        if self._current_qid not in self._question_topics:
            return
        self._question_topics[self._current_qid].pop(name, None)
        if not self._question_topics[self._current_qid]:
            del self._question_topics[self._current_qid]
            self._update_question_buttons()
        for row in self._all_toggles():
            if row.name == name:
                row.set_checked(False)
                break
        self._refresh_tags()
        for g in self.cat_groups:
            count = sum(1 for r in g.toggles if r.is_checked())
            g._update_header(count)
        self._auto_save()

    def _on_menu_handler(self, action: str, *args):
        """处理右键菜单：重命名/删除"""
        if action == "rename_cat":
            old = args[0]
            new, ok = QInputDialog.getText(self, "重命名分类", f"输入新名称:", text=old)
            if ok and new.strip() and new.strip() != old:
                self.dm.rename_category(old, new.strip())
                self._rebuild_cat_groups()
        elif action == "delete_cat":
            cat = args[0]
            reply = QMessageBox.question(self, "确认删除",
                f"确定要删除分类「{cat}」及其所有知识点吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.dm.delete_category(cat)
                self._rebuild_cat_groups()
        elif action == "rename_topic":
            cat, old = args[0], args[1]
            new, ok = QInputDialog.getText(self, "重命名知识点", f"输入新名称:", text=old)
            if ok and new.strip() and new.strip() != old:
                self.dm.rename_topic(cat, old, new.strip())
                self._rebuild_cat_groups()
        elif action == "delete_topic":
            cat, name = args[0], args[1]
            reply = QMessageBox.question(self, "确认删除",
                f"确定要删除知识点「{name}」吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.dm.delete_topic(cat, name)
                self._rebuild_cat_groups()
        if self._current_date:
            self._sync_toggles()
            self._refresh_tags()

    def _on_weight_change(self, name: str, weight: float):
        target = self._question_topics.get(self._current_qid, {})
        if name not in target:
            return
        others = [n for n in target if n != name]
        weight = max(0.01, min(0.99, weight))
        target[name] = weight

        # 总和偏离 1.0 的部分，从其他知识点按比例吸收
        other_total = sum(target[n] for n in others)
        total = weight + other_total
        if total != 1.0 and others:
            diff = 1.0 - total
            for n in others:
                share = target[n] / other_total if other_total > 0 else 1.0 / len(others)
                target[n] = round(max(0.01, target[n] + diff * share), 2)
            # 尾差修正
            target[others[-1]] = round(max(0.01, 1.0 - sum(target[n] for n in others if n != others[-1]) - weight), 2)

        # 同步各 toggle 滑块
        for row in self._all_toggles():
            if row.name in target:
                row.set_weight(target[row.name])
        self._refresh_tags()
        self._auto_save()

    def _shake_all_tags(self):
        target = self._question_topics.get(self._current_qid, {})
        chips = []
        for i in range(self.tags_layout.count()):
            item = self.tags_layout.itemAt(i)
            chip = item.widget()
            if isinstance(chip, TagChip) and chip._name in target:
                chips.append(chip)
        if not chips:
            return

        red_style = """
            QPushButton {
                background: #e74c3c; color: white; border: 2px solid #c0392b;
                border-radius: 12px; padding: 4px 10px; font-size: 12px;
            }
        """
        normal_style = """
            QPushButton {
                background: #1abc9c; color: white; border: none;
                border-radius: 12px; padding: 4px 10px; font-size: 12px;
            }
            QPushButton:hover { background: #16a085; }
        """

        for chip in chips:
            orig = chip.pos()
            anim = QPropertyAnimation(chip, b"pos")
            anim.setDuration(350)
            anim.setLoopCount(2)
            x, y = orig.x(), orig.y()
            anim.setKeyValueAt(0.0, orig)
            anim.setKeyValueAt(0.15, QPoint(x - 8, y))
            anim.setKeyValueAt(0.3, QPoint(x + 8, y))
            anim.setKeyValueAt(0.5, QPoint(x - 5, y))
            anim.setKeyValueAt(0.7, QPoint(x + 5, y))
            anim.setKeyValueAt(1.0, orig)
            anim.start(anim.DeletionPolicy.DeleteWhenStopped)

        def flash_on():
            for c in chips:
                try:
                    c.setStyleSheet(red_style)
                except RuntimeError:
                    pass

        def flash_off():
            for c in chips:
                try:
                    c.setStyleSheet(normal_style)
                except RuntimeError:
                    pass

        QTimer.singleShot(0, flash_on)
        QTimer.singleShot(150, flash_off)
        QTimer.singleShot(300, flash_on)
        QTimer.singleShot(450, flash_off)
        QTimer.singleShot(600, flash_on)
        QTimer.singleShot(800, flash_off)

    def _on_toggle(self, checked: bool):
        row = self.sender().parent()
        if not isinstance(row, ToggleRow):
            return
        if not self._current_qid:
            return
        if self._current_qid not in self._question_topics:
            self._question_topics[self._current_qid] = {}
        target = self._question_topics[self._current_qid]
        if checked:
            # 加入新知识点后自动均分权重
            new_count = len(target) + 1
            even_weight = round(1.0 / new_count, 2)
            # 调整尾差：最后一个用减法确保总和精确为 1.0
            for prev_name in target:
                target[prev_name] = even_weight
            # 新知识点占剩余份额
            remainder = round(1.0 - sum(target.values()), 2)
            target[row.name] = remainder if remainder > 0 else even_weight
            # 同步各 toggle 的滑块
            for r in self._all_toggles():
                if r.is_checked():
                    r.set_weight(target.get(r.name, even_weight))
        else:
            target.pop(row.name, None)
            if target:
                # 剩余知识点均分至 1.0
                even = round(1.0 / len(target), 2)
                for n in target:
                    target[n] = even
                target[list(target.keys())[-1]] = round(1.0 - even * (len(target) - 1), 2)
                for r in self._all_toggles():
                    if r.name in target:
                        r.set_weight(target[r.name])
            elif self._current_qid in self._question_topics:
                del self._question_topics[self._current_qid]
        self._update_question_buttons()
        self._refresh_tags()
        for g in self.cat_groups:
            if g.cat_name == row.category:
                count = sum(1 for r in g.toggles if r.is_checked())
                g._update_header(count)
                break
        self._auto_save()

    # ------------------------------------------------------------------
    # 考试列表
    # ------------------------------------------------------------------
    def _refresh_exam_list(self):
        self.exam_list.blockSignals(True)
        self.exam_list.clear()
        search = self.search_exam.text().strip()
        for dt in reversed(self.dm.dates):
            if search and search not in dt:
                continue
            meta = self.dm.get_exam_meta(dt)
            n_topics = sum(1 for q in meta.questions for _ in q.topics)
            total = f"{len(meta.questions)}题"
            if n_topics > 0:
                total += f" {n_topics}个知识点"
            item = QListWidgetItem(f"{dt}  ({total})")
            item.setData(Qt.ItemDataRole.UserRole, dt)
            self.exam_list.addItem(item)
        self.exam_list.blockSignals(False)

    def _apply_search(self):
        current = self._current_date
        self._refresh_exam_list()
        if current:
            for i in range(self.exam_list.count()):
                if self.exam_list.item(i).data(Qt.ItemDataRole.UserRole) == current:
                    self.exam_list.setCurrentRow(i)
                    break

    def _on_exam_selected(self, current, previous):
        if not current:
            return
        dt = current.data(Qt.ItemDataRole.UserRole)
        if dt == self._current_date:
            return
        # 先保存当前考试，再加载新考试
        self._auto_save()
        self._current_date = dt
        self.edit_area.setEnabled(True)
        self._load_exam(dt)

    def _load_exam(self, dt: str):
        meta = self.dm.get_exam_meta(dt)
        self.lbl_current.setText(f"当前考试: {dt}")
        # 从 exam_meta.questions 加载逐题知识点
        self._question_topics = {}
        for q in meta.questions:
            if q.topics:
                self._question_topics[q.id] = {kt.name: kt.weight for kt in q.topics}
        # 构建题目按钮
        self._build_question_buttons(meta.questions)
        # 选中第一个题目
        if meta.questions:
            self._current_qid = meta.questions[0].id
        else:
            self._current_qid = ""
        self._update_question_buttons()
        self._sync_toggles()
        self._refresh_tags()

    def _build_question_buttons(self, questions: list):
        """构建题目选择器按钮排"""
        # 清空旧按钮
        for btn in self._question_buttons:
            btn.deleteLater()
        self._question_buttons = []
        while self.qbtn_layout.count():
            self.qbtn_layout.takeAt(0)

        for q in questions:
            abbrev = self.TYPE_ABBREV.get(q.qtype, "?")
            is_obj = q.qtype in ("choice", "multi_select")
            border_color = self.OBJ_COLOR if is_obj else self.SUB_COLOR
            btn = QPushButton(f"Q{q.id} {abbrev} -")
            btn.setProperty("qid", q.id)
            btn.setProperty("qtype", q.qtype)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(32)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white; color: #95a5a6;
                    border: 2px solid {border_color};
                    border-radius: 8px;
                    padding: 4px 10px; font-size: 12px; font-weight: bold;
                }}
                QPushButton:hover {{ border-color: #1abc9c; color: #1abc9c; }}
                QPushButton:checked {{ background: #1abc9c; color: white; border-color: #16a085; }}
            """)
            btn.clicked.connect(lambda checked, qid=q.id: self._on_question_selected(qid))
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, qid=q.id, b=btn: self._on_question_menu(pos, qid, b))
            self.qbtn_layout.addWidget(btn)
            self._question_buttons.append(btn)

    def _sync_toggles(self):
        """根据当前选中题目同步所有 toggle 状态（阻断信号避免触发 _on_toggle）"""
        target = self._question_topics.get(self._current_qid, {})
        for row in self._all_toggles():
            row.toggle.blockSignals(True)
            is_sel = row.name in target
            if is_sel:
                row.set_weight(target[row.name])
            row.set_checked(is_sel)
            row.toggle.blockSignals(False)
        for g in self.cat_groups:
            count = sum(1 for r in g.toggles if r.is_checked())
            g._update_header(count)

    def _on_question_menu(self, pos, qid: str, btn: QPushButton):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: #f8f9fa; border: 1px solid #dce3e8;
                border-radius: 10px; padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px; border-radius: 6px; color: #2c3e50;
            }
            QMenu::item:selected { background: #e0f0ea; color: #16a085; }
            QMenu::separator { height: 1px; background: #dce3e8; margin: 4px 8px; }
        """)
        act_choice = menu.addAction("🔵 单选题")
        act_multi = menu.addAction("🟢 多选题")
        menu.addSeparator()
        act_fill = menu.addAction("🟠 填空题")
        act_answer = menu.addAction("🔴 解答题")
        menu.addSeparator()
        act_max = menu.addAction("✏️ 修改满分...")
        act = menu.exec(btn.mapToGlobal(pos))
        if not act:
            return
        if act == act_max:
            self._change_question_max(qid)
            return
        type_map = {act_choice: "choice", act_multi: "multi_select",
                    act_fill: "fill", act_answer: "answer"}
        new_type = type_map.get(act)
        if new_type:
            self._change_question_type(qid, new_type)

    def _change_question_max(self, qid: str):
        meta = self.dm.get_exam_meta(self._current_date)
        cur = 5.0
        for q in meta.questions:
            if q.id == qid:
                cur = q.max_score
                break
        val, ok = QInputDialog.getDouble(self, "修改满分", f"题目 Q{qid} 满分:",
                                         cur, 0.5, 50.0, 1)
        if ok:
            for q in meta.questions:
                if q.id == qid:
                    q.max_score = val
                    break
            self._build_question_buttons(meta.questions)
            self._update_question_buttons()
            self._auto_save()

    def _change_question_type(self, qid: str, new_type: str):
        meta = self.dm.get_exam_meta(self._current_date)
        for q in meta.questions:
            if q.id == qid:
                q.qtype = new_type
                break
        self._build_question_buttons(meta.questions)
        self._update_question_buttons()
        self._auto_save()

    def _all_toggles(self):
        for g in self.cat_groups:
            yield from g.toggles

    # ------------------------------------------------------------------
    # 标签刷新
    # ------------------------------------------------------------------
    def _refresh_tags(self):
        while self.tags_layout.count():
            item = self.tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        target = self._question_topics.get(self._current_qid, {})

        for name in sorted(target.keys()):
            w = target[name]
            chip = TagChip(f"{name} ({w:.2f})",
                          on_locate=self._on_tag_locate,
                          on_remove=self._on_tag_remove)
            self.tags_layout.addWidget(chip)

    # ------------------------------------------------------------------
    # 搜索
    # ------------------------------------------------------------------
    def _on_topic_search(self, text: str):
        search = text.strip()
        for g in self.cat_groups:
            if not search:
                g.body.setVisible(False)
                g._update_header(sum(1 for r in g.toggles if r.is_checked()))
                for btn in g.toggles:
                    btn.setVisible(True)
                continue
            visible = False
            for btn in g.toggles:
                match = search.lower() in btn.name.lower() or search.lower() in g.cat_name.lower()
                btn.setVisible(match)
                if match:
                    visible = True
            g.body.setVisible(visible)
            if visible:
                g.expand()

    # ------------------------------------------------------------------
    # 自动保存
    # ------------------------------------------------------------------
    def _auto_save(self):
        """保存当前考试的题目知识点到 exam_meta.xml"""
        if not self._current_date:
            return

        # 先保存当前正在编辑的题目
        current_qid = self._current_qid
        if current_qid:
            topics = {}
            for row in self._all_toggles():
                if row.is_checked():
                    topics[row.name] = row.get_weight()
            if topics:
                self._question_topics[current_qid] = topics
            elif current_qid in self._question_topics:
                del self._question_topics[current_qid]

        # 构建 Question 列表
        meta = self.dm.get_exam_meta(self._current_date)
        questions = []
        for q in meta.questions:
            topics = self._question_topics.get(q.id, {})
            kt_list = []
            for name, weight in topics.items():
                cat = "未分类"
                for c, t_list in self.dm.knowledge_pool.items():
                    if name in t_list:
                        cat = c
                        break
                kt_list.append(KnowledgeTopic(category=cat, name=name, weight=weight))
            questions.append(Question(id=q.id, qtype=q.qtype, max_score=q.max_score, topics=kt_list))
        self.dm.update_exam_questions(self._current_date, questions)

        # 更新考试列表中的题目数标记
        total = len(meta.questions)
        for i in range(self.exam_list.count()):
            item = self.exam_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == self._current_date:
                self.exam_list.blockSignals(True)
                item.setText(f"{self._current_date}  ({total}题)")
                self.exam_list.blockSignals(False)
                break

    # ------------------------------------------------------------------
    # 新增知识点
    # ------------------------------------------------------------------
    def _add_knowledge(self):
        cats = list(self.dm.knowledge_pool.keys())
        if not cats:
            return
        # 可编辑的下拉框，支持新增
        cat, ok = QInputDialog.getItem(
            self, "新增知识点",
            "选择或输入一级分类（可直接输入新分类名）:",
            cats, 0, True
        )
        if not ok or not cat:
            return
        cat = cat.strip()
        if not cat:
            return

        name, ok = QInputDialog.getText(
            self, "新增知识点",
            f"输入二级知识点名称（分类: {cat}）:"
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in self.dm.knowledge_pool.get(cat, []):
            QMessageBox.information(self, "提示", f"知识点「{name}」已存在")
            return

        self.dm.add_knowledge(cat, name)
        self._rebuild_cat_groups()
        if self._current_date:
            self._sync_toggles()
            self._refresh_tags()

    def _build_cat_groups(self):
        for i in reversed(range(self.cat_layout.count())):
            w = self.cat_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        self.cat_groups = []
        order = self.dm.category_order or list(self.dm.knowledge_pool.keys())
        for cat in order:
            if cat not in self.dm.knowledge_pool:
                continue
            topics = self.dm.knowledge_pool[cat]
            if not topics:
                continue
            group = CategoryGroup(cat, topics, on_weight_change=self._on_weight_change,
                                  on_menu=self._on_menu_handler)
            self.cat_groups.append(group)
            self.cat_layout.addWidget(group)
        for g in self.cat_groups:
            for row in g.toggles:
                row.toggle.toggled.connect(self._on_toggle)

    def _rebuild_cat_groups(self):
        self._build_cat_groups()

    def refresh(self):
        self._auto_save()
        self._refresh_exam_list()
        self._rebuild_cat_groups()
