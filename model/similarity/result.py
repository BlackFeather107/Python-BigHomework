# model/similarity/result.py

from typing import List, Tuple, Dict
from datetime import datetime
import json

class ComparisonResult:
    """
    保存两份代码的相似度比较结果。
    """
    def __init__(self,
                 file_a: str,
                 file_b: str,
                 scores: Dict[str, float],
                 segments: List[Tuple[int, int, int, int]],
                 analysis_time: datetime = None,
                 is_plagiarism: bool = False,
                 plagiarism_notes: str = ""):
        self.file_a = file_a
        self.file_b = file_b
        self.scores = scores
        self.segments = segments
        self.analysis_time = analysis_time or datetime.now()
        self.is_plagiarism = is_plagiarism
        self.plagiarism_notes = plagiarism_notes

    def to_dict(self) -> Dict:
        """转换为字典格式，用于JSON序列化"""
        return {
            'file_a': self.file_a,
            'file_b': self.file_b,
            'scores': self.scores,
            'segments': self.segments,
            'analysis_time': self.analysis_time.isoformat(),
            'is_plagiarism': self.is_plagiarism,
            'plagiarism_notes': self.plagiarism_notes
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ComparisonResult':
        """从字典格式创建实例"""
        return cls(
            file_a=data['file_a'],
            file_b=data['file_b'],
            scores=data['scores'],
            segments=data['segments'],
            analysis_time=datetime.fromisoformat(data['analysis_time']),
            is_plagiarism=data.get('is_plagiarism', False),
            plagiarism_notes=data.get('plagiarism_notes', "")
        )

class AnalysisSession:
    """
    表示一次完整的分析会话，包含所有比较结果和元数据。
    """
    def __init__(self, 
                 session_id: str,
                 directory: str,
                 analysis_time: datetime = None,
                 login_time: datetime = None):
        self.session_id = session_id
        self.directory = directory
        self.analysis_time = analysis_time or datetime.now()
        self.login_time = login_time or datetime.now()
        self.results: List[ComparisonResult] = []

    def add_result(self, result: ComparisonResult):
        """添加一个比较结果"""
        self.results.append(result)

    def get_plagiarism_results(self) -> List[ComparisonResult]:
        """获取所有被标记为抄袭的结果"""
        return [r for r in self.results if r.is_plagiarism]

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'session_id': self.session_id,
            'directory': self.directory,
            'analysis_time': self.analysis_time.isoformat(),
            'login_time': self.login_time.isoformat(),
            'results': [r.to_dict() for r in self.results]
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AnalysisSession':
        """从字典格式创建实例"""
        session = cls(
            session_id=data['session_id'],
            directory=data['directory'],
            analysis_time=datetime.fromisoformat(data['analysis_time']),
            login_time=datetime.fromisoformat(data['login_time'])
        )
        session.results = [ComparisonResult.from_dict(r) for r in data['results']]
        return session