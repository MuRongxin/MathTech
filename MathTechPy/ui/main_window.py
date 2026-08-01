"""主窗口 - 左侧导航 + 内容区切换"""
import sys

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.data_manager import DataManager
from core.logging_setup import get_logger

_log = get_logger("main_window")
from core.random_engine import RandomEngine
from .overview_tab import OverviewTab
from .random_combined_tab import RandomCombinedTab
from .score_tab import ScoreTab
from .data_maintenance_tab import DataMaintenanceTab
from .student_eval_tab import StudentEvalTab
from .data_admin_tab import DataAdminTab
from .init_dialog import InitDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MathTech - Python Edition")
        self.setMinimumSize(1360, 765)
        self.resize(1680, 945)

        # 核心业务对象
        self.dm = DataManager()
        self.random_engine = RandomEngine(self.dm)

        # 首次启动 → 初始化向导
        if getattr(self.dm, '_needs_init', False):
            dlg = InitDialog(self)
            if dlg.exec() == InitDialog.DialogCode.Accepted:
                try:
                    self.dm.reload()
                    self.dm.mark_initialized()
                except Exception as e:
                    detail = f"\n{self.dm._load_error}" if self.dm._load_error else ""
                    QMessageBox.critical(self, "加载失败",
                                         f"配置文件加载出错: {e}{detail}\n请检查 data/ 目录。")
                    sys.exit(1)
            else:
                QMessageBox.warning(self, "需要初始化",
                                    "需要先配置班级和学生数据才能使用。")
                sys.exit(0)

        # 创建中央部件
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---------- 左侧导航栏 ----------
        self.sidebar = self._build_sidebar()
        layout.addWidget(self.sidebar)

        # ---------- 内容区 ----------
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

        # 初始化各页面（顺序与导航栏一致）
        self._tabs = [
            OverviewTab(self.dm),
            RandomCombinedTab(self.dm, self.random_engine),
            ScoreTab(self.dm),
            DataMaintenanceTab(self.dm),
            StudentEvalTab(self.dm),
            DataAdminTab(self.dm),
        ]
        for tab in self._tabs:
            self.stack.addWidget(tab)

        # 成绩分析页搜索学生 → 跳转学生评估页并选中（个人趋势已迁入该页）
        self._tabs[2].on_search_student = self._goto_student_eval

        # 默认显示概览
        self.switch_tab(0)

    def _goto_student_eval(self, name: str):
        """跳转到学生评估页并选中指定学生（成绩历程视图）"""
        eval_tab = self._tabs[4]
        eval_tab.select_student(name, view="成绩历程")
        self.switch_tab(4)

    def _build_sidebar(self) -> QFrame:
        """构建左侧导航栏"""
        sidebar = QFrame()
        sidebar.setFixedWidth(180)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                padding: 15px 20px;
                text-align: left;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:checked {
                background-color: #1abc9c;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(5)

        # 标题
        title = QLabel("MathTech")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: white; padding: 10px 20px;")
        layout.addWidget(title)

        layout.addSpacing(20)

        # 导航按钮
        self.nav_buttons: list[QPushButton] = []
        nav_items = [
            ("📊 数据概览", 0),
            ("🎲 随机抽人", 1),
            ("📈 成绩分析", 2),
            ("🛠️ 数据维护", 3),
            ("🔍 学生评估", 4),
        ]
        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self.switch_tab(i))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        # 分割线
        sep = QLabel("")
        sep.setFixedHeight(1)
        sep.setStyleSheet("background: #3d566e; margin: 8px 15px;")
        layout.addWidget(sep)

        # 底部：小可爱数据维护
        self.btn_admin = QPushButton("📥 小可爱数据维护")
        self.btn_admin.setCheckable(True)
        self.btn_admin.clicked.connect(lambda checked: self.switch_tab(5))
        self.btn_admin.setStyleSheet("""
            QPushButton {
                background: transparent; color: #bdc3c7;
                border: none; padding: 10px 20px; text-align: left; font-size: 13px;
            }
            QPushButton:hover { background: #34495e; color: white; }
            QPushButton:checked { background: #1abc9c; color: white; }
        """)
        self.nav_buttons.append(self.btn_admin)
        layout.addWidget(self.btn_admin)

        layout.addStretch()

        return sidebar

    def switch_tab(self, index: int):
        """切换内容页"""
        # 切走前停止当前页可能进行中的滚动动画
        current = self.stack.currentIndex()
        if current != index and 0 <= current < len(self._tabs):
            stop = getattr(self._tabs[current], "stop_rolling", None)
            if callable(stop):
                stop()

        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        # 小可爱数据维护按钮最后单独处理
        self.btn_admin.setChecked(index == 5)

        # 通知当前 tab 刷新
        if 0 <= index < len(self._tabs):
            self._tabs[index].refresh()

    def switch_class(self, class_id: int):
        """切换班级"""
        self.dm.current_class = class_id
        _log.info("切换班级: %s", self.dm.class_names[class_id]
                  if class_id < len(self.dm.class_names) else class_id)

        # 刷新当前页面（引擎历史已按班级隔离，无需重置；
        # 切班前停止当前页可能进行中的滚动动画）
        current = self.stack.currentIndex()
        if 0 <= current < len(self._tabs):
            stop = getattr(self._tabs[current], "stop_rolling", None)
            if callable(stop):
                stop()
            self._tabs[current].refresh()
