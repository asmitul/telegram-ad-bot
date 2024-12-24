import inspect
import os
from datetime import datetime
import pytz
import traceback
from typing import Any, Optional
from wcwidth import wcswidth

COLORS = {
    "INFO": "\033[38;5;82m",     # 亮绿色
    "WARNING": "\033[38;5;214m",  # 亮橙色
    "ERROR": "\033[38;5;196m",    # 亮红色
    "DEBUG": "\033[38;5;75m",     # 天蓝色
    "MONGODB": "\033[38;5;33m",   # 深蓝色
    "TELEGRAM": "\033[38;5;51m",  # 紫色
    "RESET": "\033[0m",
    "FILENAME": "\033[38;5;240m"  # 灰色，用于文件名
}

TIMEZONE = pytz.timezone('Asia/Shanghai')


def _get_call_info(frame_offset: int = 2):
    """获取调用栈中的文件名、函数名和行号信息"""
    frame = inspect.currentframe()
    for _ in range(frame_offset):
        if frame and frame.f_back:
            frame = frame.f_back

    if frame:
        return {
            "line_number": frame.f_lineno,
            "function_name": frame.f_code.co_name,
            "filename": os.path.basename(frame.f_code.co_filename),
        }
    return {"line_number": -1, "function_name": "<unknown>", "filename": "<unknown>"}


def _format_line(line: str, width: int) -> str:
    """根据字符宽度动态填充空格，确保表格对齐"""
    line_width = wcswidth(line)
    padding = max(0, width - line_width)
    return line + " " * padding


def _format_debug_message(message: Any, level: str, frame_offset: int = 2) -> None:
    """
    格式化并输出调试信息

    Args:
        message (Any): 调试消息
        level (str): 日志级别
        frame_offset (int): 调用栈偏移量
    """
    # 获取调用栈信息
    frame = inspect.currentframe()
    for _ in range(frame_offset):
        frame = frame.f_back
    
    line_number = frame.f_lineno
    function_name = frame.f_code.co_name
    filename = os.path.basename(frame.f_code.co_filename)

    # call_info = _get_call_info(frame_offset)

    timestamp = datetime.now(TIMEZONE).strftime('%m-%d %H:%M:%S')
    color = COLORS.get(level.upper(), COLORS["INFO"])

    # print(f"\n\033[1m{'┌' + '─' * 70 + '┐'}\033[0m")
    # print(f"│ {color}{level:<7}{COLORS['RESET']} | {timestamp} | "
    #       f"{COLORS['FILENAME']}{filename}:{line_number} | {function_name}{COLORS['RESET']}")
    # print(f"├{'─' * 70}┤")

    # for line in str(message).splitlines():
    #     while line:
    #         current_line = line[:66]
    #         print(f"│ {_format_line(current_line, 68)} │")
    #         line = line[66:]

    # print(f"└{'─' * 70}┘")

    print(f"\n")
    print(f"{color}{level:<7}{COLORS['RESET']} | {timestamp}"
          f" {COLORS['FILENAME']}{filename}:{line_number} | {function_name}{COLORS['RESET']}")
    # print(f"├{'─' * 70}┤")

    for line in str(message).splitlines():
        while line:
            current_line = line[:66]
            print(f"{_format_line(current_line, 68)}")
            line = line[66:]

    # print(f"└{'─' * 70}┘")


def log_info(message: Any) -> None:
    _format_debug_message(message, "INFO")


def log_warning(message: Any) -> None:
    _format_debug_message(message, "WARNING")


def log_error(e: Exception, message: str = "操作失败", include_traceback: bool = True) -> None:
    error_message = f"{message}: {e}"
    _format_debug_message(error_message, "ERROR")

    if include_traceback:
        traceback_message = traceback.format_exc()
        _format_debug_message(f"详细错误追踪:\n{traceback_message}", "DEBUG", frame_offset=3)


def log_debug(message: Any, data: Optional[dict] = None) -> None:
    debug_message = str(message)
    if data:
        debug_message += f"\n数据: {data}"
    _format_debug_message(debug_message, "DEBUG")


def log_mongodb(message: Any) -> None:
    _format_debug_message(message, "MONGODB")


def log_telegram(message: Any) -> None:
    _format_debug_message(message, "TELEGRAM")


if __name__ == "__main__":
    log_info("Hello, World!")
    log_warning("This is a warning message.")
    log_error(Exception("An error occurred"), "An error occurred")
    log_debug("This is a debug message", {"key": "value"})
    log_mongodb("This is a MongoDB message")
    log_telegram("This is a Telegram message")