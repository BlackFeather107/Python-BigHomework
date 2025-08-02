# model/file_manager.py

from pathlib import Path
from typing import List, Set # self.files 被初始化为Set， 而不是List

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
        # --- 调试打印 1 ---
        print(f"[DEBUG FileManager] 在目录 {directory} 中找到 {len(new_files)} 个新文件。")
        
        self.files.update(new_files)

        # --- 调试打印 2 ---
        print(f"[DEBUG FileManager] 更新后，FileManager中总文件数: {len(self.files)}")

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