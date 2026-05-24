"""
为整个项目提供统一的绝对路径。

这个文件基本照参考项目写法保留。
"""

import os
from pathlib import Path


def get_project_root() -> str:
    """
    获取工程根目录。
    """
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    return project_root


def get_abs_path(relative_path: str) -> str:
    """
    输入相对路径，返回基于项目根目录的绝对路径。
    """
    return os.path.join(get_project_root(), relative_path)


def sanitize_filename(filename: str) -> str:
    """
    清洗上传文件名，防止路径穿越攻击。

    - 去除所有目录组件（../, /, \\）
    - 拒绝空文件名或以 . 开头的隐藏文件名
    """
    if not filename:
        raise ValueError("文件名不能为空。")

    name = Path(filename).name

    if not name or name.startswith("."):
        raise ValueError(f"不合法的文件名：{filename}")

    return name
