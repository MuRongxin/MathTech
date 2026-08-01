"""轻量日志体系（stdlib logging，无第三方依赖）

设计（贴合本项目单人桌面应用场景，刻意保持简单）：
- 双通道：控制台 + 滚动文件 data/logs/mathtech.log（1MB × 3 个滚动）
- 级别：默认 INFO；环境变量 MATHTECH_DEBUG=1 开 DEBUG（含数据写回审计）
- main() 启动时 setup_logging() 并 hook_uncaught_exceptions()
- 各模块用 get_logger(__name__) 获取子日志器；未初始化时自动退回
  logging 的 lastResort 行为（stderr），不会报错

明确不做：JSON 结构化、按模块分文件、远程上报、第三方库。
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_ROOT_NAME = "mathtech"
_LOG_DIR = Path(__file__).parent.parent / "data" / "logs"
_initialized = False


def get_logger(name: str = None) -> logging.Logger:
    """获取 mathtech 子日志器（传模块名便于定位，如 get_logger("data_manager")）"""
    if not name:
        return logging.getLogger(_ROOT_NAME)
    return logging.getLogger(f"{_ROOT_NAME}.{name}")


def setup_logging() -> Path:
    """初始化双通道日志，返回日志文件路径（幂等）"""
    global _initialized
    log_path = _LOG_DIR / "mathtech.log"
    if _initialized:
        return log_path
    _initialized = True

    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    debug = os.environ.get("MATHTECH_DEBUG") == "1"

    root = logging.getLogger(_ROOT_NAME)
    root.setLevel(logging.DEBUG if debug else logging.INFO)
    root.propagate = False  # 不向 root logger 传播，避免重复输出

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                            "%Y-%m-%d %H:%M:%S")

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    root.addHandler(ch)

    fh = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=3,
                             encoding="utf-8")
    fh.setFormatter(fmt)
    root.addHandler(fh)

    root.info("日志系统初始化（级别=%s，文件=%s）",
              "DEBUG" if debug else "INFO", log_path)
    return log_path


def hook_uncaught_exceptions() -> None:
    """把未捕获异常（含 Qt 槽函数穿透出来的）记入日志而非只进 stderr"""
    def _hook(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        get_logger().error("未捕获异常", exc_info=(exc_type, exc_value, exc_tb))
    sys.excepthook = _hook
