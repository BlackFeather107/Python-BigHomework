# model/file_manager.py

from pathlib import Path
from typing import List

class FileManager:
    def __init__(self):
        # 存储所有待查重的文件路径
        self.files: List[Path] = []

    def load_directory(self, directory: str) -> None:
        """
        扫描指定目录，批量导入所有以 .py 结尾的文件。
        :param directory: 目标文件夹路径
        """
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{directory} 不是有效目录")
        # 递归搜索 .py 文件
        self.files = [p for p in dir_path.rglob('*.py') if p.is_file()]

    def read_file(self, filepath: Path) -> str:
        """
        读取指定文件的源码内容。
        :param filepath: 文件路径对象
        :return: 源码文本
        """
        try:
            return filepath.read_text(encoding='utf-8')
        except Exception as e:
            raise IOError(f"读取文件 {filepath} 失败: {e}")