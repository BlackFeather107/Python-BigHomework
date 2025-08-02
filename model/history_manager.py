# model/history_manager.py

import json
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from .similarity.result import AnalysisSession, ComparisonResult

class HistoryManager:
    """
    管理分析历史记录，负责保存和加载分析会话。
    """
    def __init__(self, history_file: str = "history/analysis_history.json"):
        self.history_file = Path(history_file)
        self.history_file.parent.mkdir(exist_ok=True)
        self.sessions: List[AnalysisSession] = []
        self.load_history()

    def load_history(self):
        """从文件加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = [AnalysisSession.from_dict(session_data) 
                                   for session_data in data.get('sessions', [])]
            except Exception as e:
                print(f"加载历史记录失败: {e}")
                self.sessions = []

    def save_history(self):
        """保存历史记录到文件"""
        try:
            data = {
                'sessions': [session.to_dict() for session in self.sessions],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    def add_session(self, session: AnalysisSession):
        """添加新的分析会话"""
        self.sessions.append(session)
        self.save_history()

    def get_all_sessions(self) -> List[AnalysisSession]:
        """获取所有分析会话"""
        return self.sessions

    def get_session_by_id(self, session_id: str) -> Optional[AnalysisSession]:
        """根据会话ID获取会话"""
        for session in self.sessions:
            if session.session_id == session_id:
                return session
        return None

    def get_plagiarism_sessions(self) -> List[AnalysisSession]:
        """获取包含抄袭判定的会话"""
        return [session for session in self.sessions 
                if session.get_plagiarism_results()]

    def update_result_plagiarism_status(self, session_id: str, 
                                      file_a: str, file_b: str, 
                                      is_plagiarism: bool, notes: str = ""):
        """更新特定结果的抄袭状态"""
        session = self.get_session_by_id(session_id)
        if session:
            for result in session.results:
                if (result.file_a == file_a and result.file_b == file_b) or \
                   (result.file_a == file_b and result.file_b == file_a):
                    result.is_plagiarism = is_plagiarism
                    result.plagiarism_notes = notes
                    break
            self.save_history()

    def export_plagiarism_report(self, output_file: str) -> bool:
        """导出所有抄袭判定的报告"""
        try:
            plagiarism_results = []
            for session in self.sessions:
                for result in session.get_plagiarism_results():
                    plagiarism_results.append({
                        'session_id': session.session_id,
                        'analysis_time': session.analysis_time.isoformat(),
                        'file_a': result.file_a,
                        'file_b': result.file_b,
                        'scores': result.scores,
                        'notes': result.plagiarism_notes
                    })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(plagiarism_results, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出抄袭报告失败: {e}")
            return False

    def export_plagiarism_files(self, output_dir: str) -> bool:
        """导出所有被判定抄袭的代码文件"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            exported_files = set()
            for session in self.sessions:
                for result in session.get_plagiarism_results():
                    # 导出文件A
                    if result.file_a not in exported_files:
                        self._export_file(result.file_a, output_path)
                        exported_files.add(result.file_a)
                    
                    # 导出文件B
                    if result.file_b not in exported_files:
                        self._export_file(result.file_b, output_path)
                        exported_files.add(result.file_b)
            
            return True
        except Exception as e:
            print(f"导出抄袭文件失败: {e}")
            return False

    def _export_file(self, source_file: str, output_dir: Path):
        """导出单个文件"""
        try:
            source_path = Path(source_file)
            if source_path.exists():
                # 创建带时间戳的文件名以避免冲突
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{source_path.name}"
                target_path = output_dir / filename
                
                # 复制文件内容
                with open(source_path, 'r', encoding='utf-8') as src:
                    content = src.read()
                
                with open(target_path, 'w', encoding='utf-8') as dst:
                    dst.write(content)
        except Exception as e:
            print(f"导出文件 {source_file} 失败: {e}")

    def clear_history(self):
        """清空历史记录"""
        self.sessions = []
        self.save_history() 