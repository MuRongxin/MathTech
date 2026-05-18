"""数据维护页面 — 考试知识点管理"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QFrame, QMessageBox,
    QInputDialog, QScrollArea, QButtonGroup
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from core.data_manager import DataManager
from core.models import KnowledgeTopic


class TagChip(QPushButton):
    """可删除的知识点标签"""

    def __init__(self, text: str, on_remove, parent=None):
        super().__init__(f"× {text}", parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background: #1abc9c; color: white; border: none;
                border-radius: 12px; padding: 4px 10px; font-size: 12px;
            }
            QPushButton:hover { background: #e74c3c; }
        """)
        self.clicked.connect(lambda: on_remove(text))


class TopicToggle(QPushButton):
    """知识点选择按钮"""

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


class CategoryGroup(QWidget):
    """一类知识点的折叠组"""

    def __init__(self, cat_name: str, topics: list[str], parent=None):
        super().__init__(parent)
        self.cat_name = cat_name

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.header = QPushButton()
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header.setStyleSheet("""
            QPushButton {
                background: transparent; border: none; text-align: left;
                padding: 6px 4px; font-size: 13px; font-weight: bold; color: #2c3e50;
            }
            QPushButton:hover { color: #1abc9c; }
        """)
        self.header.clicked.connect(self._toggle)
        layout.addWidget(self.header)

        self.body = QWidget()
        self.body.setStyleSheet("background: transparent;")
        self.body.setVisible(False)
        from ui.random_tab import FlowLayout
        self.body_layout = FlowLayout(self.body, 6)
        self.body_layout.setContentsMargins(8, 2, 8, 2)
        self.toggles: list[TopicToggle] = []

        for t in topics:
            btn = TopicToggle(cat_name, t)
            self.body_layout.addWidget(btn)
            self.toggles.append(btn)

        layout.addWidget(self.body)
        self._update_header()

    def _toggle(self):
        self.body.setVisible(not self.body.isVisible())
        self._update_header()

    def expand(self):
        self.body.setVisible(True)
        self._update_header()

    def _update_header(self, selected_count: int = 0):
        arrow = "▼" if self.body.isVisible() else "▶"
        total = len(self.toggles)
        cnt_str = f"({selected_count}/{total})" if selected_count > 0 else f"({total})"
        self.header.setText(f"{arrow} {self.cat_name} {cnt_str}")

    def set_selected(self, selected_names: set[str]):
        count = 0
        for btn in self.toggles:
            is_sel = btn.name in selected_names
            btn.setChecked(is_sel)
            btn._update_style()
            if is_sel:
                count += 1
        self._update_header(count)


class DataMaintenanceTab(QWidget):
    """数据维护页 — 模式切换选择为主客观部分添加知识点"""

    MODE_KEYS = ["subjective_topics", "objective_topics"]
    MODE_LABELS = ["客观题涉及知识点", "主观题涉及知识点"]
    MODE_COLORS = ["#3498db", "#e67e22"]

    def __init__(self, dm: DataManager):
        super().__init__()
        self.dm = dm
        self._current_date = ""
        self._active_mode = 0  # 0=客观题, 1=主观题

        # 当前考试的两种知识点集合
        self._sub_selected: set[str] = set()
        self._obj_selected: set[str] = set()

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
            }
            QListWidget::item:hover { background: #e8f8f5; }
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

        # ---- 模式切换（居中） ----
        mode_row = QHBoxLayout()
        mode_row.addStretch()
        self.mode_btns = QButtonGroup(self)
        self.mode_btn_widgets = []
        for i, label in enumerate(self.MODE_LABELS):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(i == 0)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(34)
            btn.setFixedWidth(160)
            color = self.MODE_COLORS[i]
            if i == 0:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {color}; color: white;
                        border: 2px solid {color}; border-right: none;
                        padding: 6px 16px; font-size: 13px; font-weight: bold;
                        border-radius: 17px 0 0 17px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent; color: {color};
                        border: 2px solid {color};
                        padding: 6px 16px; font-size: 13px; font-weight: bold;
                        border-radius: 0 17px 17px 0;
                    }}
                """)
            self.mode_btns.addButton(btn, i)
            btn.clicked.connect(lambda checked, idx=i: self._switch_mode(idx))
            mode_row.addWidget(btn)
            self.mode_btn_widgets.append(btn)
        mode_row.addStretch()
        right_layout.addLayout(mode_row)

        # ---- 已选标签 ----
        tags_frame = QFrame()
        tags_frame.setStyleSheet("background: white; border-radius: 8px;")
        from ui.random_tab import FlowLayout
        self.tags_layout = FlowLayout(tags_frame, 8)
        self.tags_layout.setContentsMargins(12, 10, 12, 10)
        right_layout.addWidget(tags_frame)

        # ---- 滚动区：知识点选择 ----
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(6)

        self.search_topic = QLineEdit()
        self.search_topic.setPlaceholderText("🔍 搜索知识点（支持模糊匹配）...")
        self.search_topic.setStyleSheet("""
            QLineEdit {
                border: 2px solid #dfe6e9; border-radius: 8px;
                padding: 8px 12px; font-size: 13px; background: white;
            }
            QLineEdit:focus { border-color: #1abc9c; }
        """)
        self.search_topic.textChanged.connect(self._on_topic_search)
        scroll_layout.addWidget(self.search_topic)

        # 分类组
        self.cat_groups: list[CategoryGroup] = []
        self.cat_container = QWidget()
        self.cat_container.setStyleSheet("background: transparent;")
        self.cat_layout = QVBoxLayout(self.cat_container)
        self.cat_layout.setContentsMargins(0, 0, 0, 0)
        self.cat_layout.setSpacing(2)

        for cat in self.dm.knowledge_pool:
            topics = self.dm.knowledge_pool[cat]
            if not topics:
                continue
            group = CategoryGroup(cat, topics)
            self.cat_groups.append(group)
            self.cat_layout.addWidget(group)

        for g in self.cat_groups:
            for btn in g.toggles:
                btn.toggled.connect(self._on_toggle)

        scroll_layout.addWidget(self.cat_container)
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        right_layout.addWidget(scroll, 1)

        # ---- 底部按钮 ----
        bottom = QHBoxLayout()
        bottom.addStretch()

        self.btn_add_topic = QPushButton("＋ 新增知识点")
        self.btn_add_topic.setMinimumSize(130, 38)
        self.btn_add_topic.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_topic.setStyleSheet("""
            QPushButton {
                background: #3498db; color: white; border: none;
                border-radius: 19px; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #2980b9; }
        """)
        self.btn_add_topic.clicked.connect(self._add_knowledge)
        bottom.addWidget(self.btn_add_topic)

        bottom.addSpacing(12)

        self.btn_save = QPushButton("💾 保存")
        self.btn_save.setMinimumSize(120, 38)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1abc9c, stop:1 #16a085);
                color: white; border: none; border-radius: 19px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1dd2af, stop:1 #1abc9c); }
        """)
        self.btn_save.clicked.connect(self._save)
        bottom.addWidget(self.btn_save)

        bottom.addSpacing(12)

        self.btn_clear = QPushButton("🗑️ 清空当前")
        self.btn_clear.setMinimumSize(100, 38)
        self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background: white; color: #e74c3c; border: 2px solid #e74c3c;
                border-radius: 19px; font-size: 13px;
            }
            QPushButton:hover { background: #e74c3c; color: white; }
        """)
        self.btn_clear.clicked.connect(self._clear_mode)
        bottom.addWidget(self.btn_clear)

        bottom.addStretch()
        right_layout.addLayout(bottom)
        layout.addWidget(right, 1)

        self._refresh_exam_list()

    # ------------------------------------------------------------------
    # 模式切换
    # ------------------------------------------------------------------
    def _switch_mode(self, idx: int):
        if idx == self._active_mode:
            return
        prev = self._active_mode
        self._active_mode = idx

        # 更新按钮样式
        for i, btn in enumerate(self.mode_btn_widgets):
            c = self.MODE_COLORS[i]
            if i == idx:
                # 选中：实心
                if i == 0:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background: {c}; color: white;
                            border: 2px solid {c}; border-right: none;
                            padding: 6px 16px; font-size: 13px; font-weight: bold;
                            border-radius: 17px 0 0 17px;
                        }}
                    """)
                else:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background: {c}; color: white;
                            border: 2px solid {c};
                            padding: 6px 16px; font-size: 13px; font-weight: bold;
                            border-radius: 0 17px 17px 0;
                        }}
                    """)
            else:
                # 未选中：空心
                if i == 0:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background: transparent; color: {c};
                            border: 2px solid {c}; border-right: none;
                            padding: 6px 16px; font-size: 13px; font-weight: bold;
                            border-radius: 17px 0 0 17px;
                        }}
                    """)
                else:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background: transparent; color: {c};
                            border: 2px solid {c};
                            padding: 6px 16px; font-size: 13px; font-weight: bold;
                            border-radius: 0 17px 17px 0;
                        }}
                    """)

        self._sync_toggles()
        self._refresh_tags()

    # ------------------------------------------------------------------
    # 知识点切换
    # ------------------------------------------------------------------
    def _on_toggle(self, checked: bool):
        btn = self.sender()
        if not isinstance(btn, TopicToggle):
            return

        target = self._sub_selected if self._active_mode == 0 else self._obj_selected
        if checked:
            target.add(btn.name)
        else:
            target.discard(btn.name)

        self._refresh_tags()
        # 更新分类标题计数
        for g in self.cat_groups:
            if g.cat_name == btn.category:
                sel = self._sub_selected if self._active_mode == 0 else self._obj_selected
                count = sum(1 for b in g.toggles if b.isChecked())
                g._update_header(count)
                break

    # ------------------------------------------------------------------
    # 考试列表
    # ------------------------------------------------------------------
    def _refresh_exam_list(self):
        self.exam_list.blockSignals(True)
        self.exam_list.clear()
        search = self.search_exam.text().strip()
        for dt in self.dm.dates:
            if search and search not in dt:
                continue
            meta = self.dm.get_exam_meta(dt)
            total = len(meta.subjective_topics) + len(meta.objective_topics)
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
        self._current_date = dt
        self._load_exam(dt)

    def _load_exam(self, dt: str):
        meta = self.dm.get_exam_meta(dt)
        self.lbl_current.setText(f"当前考试: {dt}")

        # 缓存两份知识点名
        self._sub_selected = {kt.name for kt in meta.subjective_topics}
        self._obj_selected = {kt.name for kt in meta.objective_topics}

        self._sync_toggles()
        self._refresh_tags()

    def _sync_toggles(self):
        """根据当前模式同步所有 toggle 状态"""
        target = self._sub_selected if self._active_mode == 0 else self._obj_selected
        for btn in self._all_toggles():
            is_sel = btn.name in target
            btn.setChecked(is_sel)
            btn._update_style()
        for g in self.cat_groups:
            sel = self._sub_selected if self._active_mode == 0 else self._obj_selected
            count = sum(1 for b in g.toggles if b.name in sel)
            g._update_header(count)

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

        target = self._sub_selected if self._active_mode == 0 else self._obj_selected
        mode_name = self.MODE_LABELS[self._active_mode]

        def remove_cb(name: str):
            target.discard(name)
            # 同步 toggle
            for btn in self._all_toggles():
                if btn.name == name:
                    btn.setChecked(False)
                    btn._update_style()
                    break
            self._refresh_tags()
            # 更新分类计数
            for g in self.cat_groups:
                sel = self._sub_selected if self._active_mode == 0 else self._obj_selected
                count = sum(1 for b in g.toggles if b.isChecked())
                g._update_header(count)

        for name in sorted(target):
            self.tags_layout.addWidget(TagChip(name, remove_cb))

    # ------------------------------------------------------------------
    # 搜索
    # ------------------------------------------------------------------
    def _on_topic_search(self, text: str):
        search = text.strip()
        for g in self.cat_groups:
            if not search:
                g.body.setVisible(False)
                g._update_header(sum(1 for b in g.toggles if b.isChecked()))
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
    # 保存 / 清空 / 新增
    # ------------------------------------------------------------------
    def _save(self):
        if not self._current_date:
            return

        # 从缓存构建 KnowledgeTopic 列表
        sub_topics = []
        obj_topics = []
        for g in self.cat_groups:
            for btn in g.toggles:
                if btn.name in self._sub_selected:
                    sub_topics.append(KnowledgeTopic(btn.category, btn.name))
                if btn.name in self._obj_selected:
                    obj_topics.append(KnowledgeTopic(btn.category, btn.name))

        self.dm.update_exam_meta(self._current_date, sub_topics, obj_topics)

        total = len(sub_topics) + len(obj_topics)
        for i in range(self.exam_list.count()):
            item = self.exam_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == self._current_date:
                self.exam_list.blockSignals(True)
                item.setText(f"{self._current_date}  ({total})")
                self.exam_list.blockSignals(False)
                break
        self.lbl_current.setText(f"当前考试: {self._current_date}  ✅ 已保存")

    def _clear_mode(self):
        if not self._current_date:
            return
        label = self.MODE_LABELS[self._active_mode]
        reply = QMessageBox.question(
            self, "确认清空",
            f"确定要清空当前考试的「{label}」吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        target = self._sub_selected if self._active_mode == 0 else self._obj_selected
        target.clear()
        self._sync_toggles()
        self._refresh_tags()

    def _add_knowledge(self):
        cats = list(self.dm.knowledge_pool.keys())
        if not cats:
            return
        cat, ok = QInputDialog.getItem(
            self, "新增知识点", "选择一级分类:", cats, 0, False
        )
        if not ok or not cat:
            return
        name, ok = QInputDialog.getText(
            self, "新增知识点", f"输入二级知识点名称 (分类: {cat}):"
        )
        if not ok or not name.strip():
            return
        name = name.strip()
        if name in self.dm.knowledge_pool.get(cat, []):
            QMessageBox.information(self, "提示", f"知识点「{name}」已存在")
            return

        self.dm.add_knowledge(cat, name)
        # 重建分类组
        self._rebuild_cat_groups()
        if self._current_date:
            self._sync_toggles()
            self._refresh_tags()

    def _rebuild_cat_groups(self):
        for i in reversed(range(self.cat_layout.count())):
            w = self.cat_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        self.cat_groups = []
        for cat in self.dm.knowledge_pool:
            topics = self.dm.knowledge_pool[cat]
            if not topics:
                continue
            group = CategoryGroup(cat, topics)
            self.cat_groups.append(group)
            self.cat_layout.addWidget(group)

        for g in self.cat_groups:
            for btn in g.toggles:
                btn.toggled.connect(self._on_toggle)

    def refresh(self):
        self._refresh_exam_list()
        self._rebuild_cat_groups()
