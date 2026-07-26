"""主窗口 - 左侧导航 + 内容区切换"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from core.data_manager import DataManager
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
                self.dm._needs_init = False
                try:
                    self.dm._load_all()
                except Exception as e:
                    QMessageBox.critical(self, "加载失败",
                                         f"配置文件加载出错: {e}\n请检查 data/ 目录。")
                    import sys
                    sys.exit(1)
                self.dm._load_question_scores()
                self.dm._validate()
                self.dm._initialized = True
            else:
                QMessageBox.warning(self, "需要初始化",
                                    "需要先配置班级和学生数据才能使用。")
                import sys
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

        # 默认显示概览
        self.switch_tab(0)

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
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
        # 小可爱数据维护按钮最后单独处理
        self.btn_admin.setChecked(index == 6)

        # 通知当前 tab 刷新
        if 0 <= index < len(self._tabs):
            self._tabs[index].refresh()

    def switch_class(self, class_id: int):
        """切换班级"""
        self.dm.current_class = class_id

        # 清空随机历史（切换班级时重置，避免混淆）
        self.random_engine.reset_history()

        # 刷新当前页面
        current = self.stack.currentIndex()
        if 0 <= current < len(self._tabs):
            self._tabs[current].refresh()
