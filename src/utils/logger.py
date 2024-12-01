import inspect
import os
from datetime import datetime
import pytz
import traceback
from typing import Any, Optional

def _format_debug_message(
    message: Any, 
    level: str = "INFO",
    frame_offset: int = 2
) -> None:
    """
    格式化调试信息的内部函数
    
    Args:
        message (Any): 调试消息（支持任何可转为字符串的类型）
        level (str): 日志级别
        frame_offset (int): 调用栈偏移量，用于准确定位调用位置
    """
    # 获取调用栈信息
    frame = inspect.currentframe()
    for _ in range(frame_offset):
        frame = frame.f_back
    
    line_number = frame.f_lineno
    function_name = frame.f_code.co_name
    filename = os.path.basename(frame.f_code.co_filename)
    
    # 获取当前时间戳 (UTC+8)
    tz = pytz.timezone('Asia/Shanghai')
    timestamp = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
    
    # ANSI 颜色代码
    colors = {
        "INFO": "\033[38;5;82m",     # 亮绿色
        "WARNING": "\033[38;5;214m",  # 亮橙色
        "ERROR": "\033[38;5;196m",    # 亮红色
        "DEBUG": "\033[38;5;75m",     # 天蓝色
        "RESET": "\033[0m",
        "FILENAME": "\033[38;5;240m"  # 灰色，用于文件名
    }
    
    level = level.upper()
    color = colors.get(level, colors["INFO"])
    
    # 美化输出格式
    print(f"\n┌{'─' * 70}┐")
    print(
        f"│ {color}{level:<7}{colors['RESET']} | "
        f"{timestamp} | "
        f"{colors['FILENAME']}{filename}:{line_number}{colors['RESET']} │"
    )
    print(f"│ {function_name:<68} │")
    print(f"├{'─' * 70}┤")
    
    # 处理多行消息
    message_lines = str(message).split('\n')
    for line in message_lines:
        while line:
            current_line = line[:66]  # 留出边距
            print(f"│ {current_line:<68} │")
            line = line[66:]
    
    print(f"└{'─' * 70}┘")

def log_info(message: Any) -> None:
    """
    记录普通信息
    用于记录程序的常规操作信息，如用户操作、状态变化等
    
    Args:
        message: 要记录的信息（支持任何可转为字符串的类型）
    """
    _format_debug_message(message, "INFO")

def log_warning(message: Any) -> None:
    """
    记录警告信息
    用于记录需要注意但不影响程序运行的问题，如性能问题、重试操作等
    
    Args:
        message: 警告信息（支持任何可转为字符串的类型）
    """
    _format_debug_message(message, "WARNING")

def log_error(
    e: Exception, 
    message: str = "操作失败",
    include_traceback: bool = True
) -> None:
    """
    记录错误信息
    用于记录操作失败或发生错误的情况
    
    Args:
        e (Exception): 异常对象
        message (str): 错误描述信息
        include_traceback (bool): 是否包含详细的错误追踪信息
    """
    error_message = f"{message}: {str(e)}"
    _format_debug_message(error_message, "ERROR")
    
    if include_traceback:
        _format_debug_message(
            f"详细错误追踪:\n{traceback.format_exc()}", 
            "DEBUG",
            frame_offset=3
        )

def log_debug(
    message: Any,
    data: Optional[dict] = None
) -> None:
    """
    记录调试信息
    用于记录详细的调试信息，如变量值、执行流程等
    
    Args:
        message: 调试信息（支持任何可转为字符串的类型）
        data (dict, optional): 额外的调试数据
    """
    debug_message = str(message)
    if data:
        debug_message += "\n数据: " + str(data)
    _format_debug_message(debug_message, "DEBUG")


# 测试示例
if __name__ == "__main__":
    try:
        # 测试不同级别的日志
        log_info("用户 John Doe 已登录系统")
        log_warning("API 响应时间: 2.5秒，超过预期")
        
        # 测试带额外数据的调试日志
        user_data = {
            "id": 12345,
            "name": "John Doe",
            "status": "active"
        }
        log_debug("用户状态检查", data=user_data)
        
        # 测试错误日志
        # raise ValueError("无效的用户ID")
    except Exception as e:
        log_error(e, "用户验证失败")