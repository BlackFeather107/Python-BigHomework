# model/file_manager.py

from pathlib import Path
from typing import List, Set

class FileManager:
    def __init__(self):
        # 存储所有待查重的文件路径
        self.files: Set[Path] = set()

    def load_directory(self, directory: str) -> None:
        """
        扫描指定目录，将所有 .py 文件添加到现有文件集合中。
        """
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{directory} 不是有效目录")
        # 递归搜索 .py 文件
        new_files = {p for p in dir_path.rglob('*.py') if p.is_file()}
        
        self.files.update(new_files)

    def load_files(self, file_paths: List[str]) -> None:
        """
        接收一个文件路径列表，验证后添加到现有文件集合中。
        """
        for file_path in file_paths:
            p = Path(file_path)
            # 确保是文件、存在且是.py文件
            if p.is_file() and p.suffix == '.py':
                self.files.add(p)

    def remove_file(self, file_path_to_remove: Path) -> None:
        """从集合中移除指定的文件路径。"""
        self.files.discard(file_path_to_remove)

    def clear_all(self) -> None:
        """清空所有已导入的文件。"""
        self.files.clear()

    @property
    def sorted_files(self) -> List[Path]:
        """
        提供一个按字母顺序排序后的文件列表，方便外部调用。
        """
        return sorted(list(self.files))

    def read_file(self, filepath: Path) -> str:
        """
        读取指定文件的源码内容。
        """
        try:
            return filepath.read_text(encoding='utf-8')
        except Exception as e:
            raise IOError(f"读取文件 {filepath} 失败: {e}")