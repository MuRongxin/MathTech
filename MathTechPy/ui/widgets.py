"""共用 UI 组件"""
from PyQt6.QtWidgets import QLayout, QLayoutItem
from PyQt6.QtCore import Qt, QSize, QRect, QPoint


class FlowLayout(QLayout):
    """自动换行的流式布局"""

    def __init__(self, parent=None, spacing=8):
        QLayout.__init__(self, parent)
        self._items: list[QLayoutItem] = []
        self._spacing = spacing
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item: QLayoutItem):
        self._items.append(item)

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index: int):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width: int):
        return self._do_layout(QRect(0, 0, width, 0), dry_run=True)

    def minimumSize(self):
        s = QSize(0, 0)
        for item in self._items:
            s = s.expandedTo(item.minimumSize())
        return s

    def sizeHint(self):
        if self._items and self.parentWidget():
            w = self.parentWidget().width()
            if w > 0:
                h = self._do_layout(QRect(0, 0, w, 0), dry_run=True)
                return QSize(w, h)
        return self.minimumSize()

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        self._do_layout(rect, dry_run=False)

    def _do_layout(self, rect: QRect, dry_run: bool):
        x = rect.x()
        y = rect.y()
        line_height = 0

        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + self._spacing
            if next_x > rect.right() + 1 and x > rect.x():
                x = rect.x()
                y += line_height + self._spacing
                line_height = 0
                next_x = x + hint.width() + self._spacing

            if not dry_run:
                item.setGeometry(QRect(QPoint(x, y), hint))

            x = next_x
            line_height = max(line_height, hint.height())

        return y + line_height - rect.y()
