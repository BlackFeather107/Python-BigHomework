#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
演示新功能的脚本
展示历史记录、抄袭判定和导出功能的使用方法
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from model.history_manager import HistoryManager
from model.similarity.result import AnalysisSession, ComparisonResult
from datetime import datetime
import json

def demo_history_features():
    """演示历史记录功能"""
    print("=== 历史记录功能演示 ===")
    
    # 创建历史记录管理器
    history_manager = HistoryManager("demo_history.json")
    
    # 创建模拟的分析会话
    session1 = AnalysisSession(
        session_id="demo_session_001",
        directory="/demo/student_assignments",
        login_time=datetime.now()
    )
    
    # 添加一些模拟的查重结果
    results = [
        ComparisonResult(
            file_a="/demo/student1.py",
            file_b="/demo/student2.py",
            scores={"综合可疑度": 0.95, "逻辑顺序相似度": 0.98},
            segments=[(0, 50, 0, 50)],
            analysis_time=datetime.now(),
            is_plagiarism=True,
            plagiarism_notes="代码结构几乎完全相同，变量名也高度相似"
        ),
        ComparisonResult(
            file_a="/demo/student1.py",
            file_b="/demo/student3.py",
            scores={"综合可疑度": 0.45, "逻辑顺序相似度": 0.50},
            segments=[(10, 30, 15, 35)],
            analysis_time=datetime.now(),
            is_plagiarism=False,
            plagiarism_notes=""
        ),
        ComparisonResult(
            file_a="/demo/student2.py",
            file_b="/demo/student3.py",
            scores={"综合可疑度": 0.75, "逻辑顺序相似度": 0.80},
            segments=[(5, 40, 8, 43)],
            analysis_time=datetime.now(),
            is_plagiarism=True,
            plagiarism_notes="部分代码段存在明显抄袭"
        )
    ]
    
    for result in results:
        session1.add_result(result)
    
    # 保存会话
    history_manager.add_session(session1)
    print(f"✓ 已保存分析会话: {session1.session_id}")
    print(f"✓ 会话包含 {len(session1.results)} 个比较结果")
    
    # 演示加载历史记录
    all_sessions = history_manager.get_all_sessions()
    print(f"✓ 加载了 {len(all_sessions)} 个历史会话")
    
    # 演示获取抄袭会话
    plagiarism_sessions = history_manager.get_plagiarism_sessions()
    print(f"✓ 发现 {len(plagiarism_sessions)} 个包含抄袭判定的会话")
    
    return history_manager

def demo_plagiarism_management():
    """演示抄袭管理功能"""
    print("\n=== 抄袭管理功能演示 ===")
    
    history_manager = HistoryManager("demo_history.json")
    
    # 演示更新抄袭状态
    history_manager.update_result_plagiarism_status(
        "demo_session_001",
        "/demo/student1.py",
        "/demo/student3.py",
        True,
        "经过人工审查，确认为抄袭"
    )
    print("✓ 已更新抄袭判定状态")
    
    # 演示获取抄袭结果
    session = history_manager.get_session_by_id("demo_session_001")
    if session:
        plagiarism_results = session.get_plagiarism_results()
        print(f"✓ 该会话包含 {len(plagiarism_results)} 个抄袭判定")
        
        for result in plagiarism_results:
            print(f"  - {Path(result.file_a).name} vs {Path(result.file_b).name}")
            print(f"    综合可疑度: {result.scores.get('综合可疑度', 0):.2%}")
            print(f"    备注: {result.plagiarism_notes}")

def demo_export_features():
    """演示导出功能"""
    print("\n=== 导出功能演示 ===")
    
    history_manager = HistoryManager("demo_history.json")
    
    # 演示导出抄袭报告
    report_file = "demo_plagiarism_report.json"
    if history_manager.export_plagiarism_report(report_file):
        print(f"✓ 抄袭报告已导出到: {report_file}")
        
        # 显示报告内容
        with open(report_file, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
            print(f"✓ 报告包含 {len(report_data)} 个抄袭记录")
    else:
        print("✗ 导出抄袭报告失败")
    
    # 演示导出抄袭文件（模拟）
    print("✓ 抄袭文件导出功能已准备就绪")
    print("  注意：实际导出需要真实的文件路径")

def demo_gui_features():
    """演示GUI功能"""
    print("\n=== GUI功能演示 ===")
    print("✓ 登录时间显示：程序启动时自动记录并显示")
    print("✓ 历史记录面板：左侧显示所有分析会话")
    print("✓ 右键菜单：在结果列表中右键可标记抄袭")
    print("✓ 抄袭状态列：显示每对文件的抄袭判定状态")
    print("✓ 标签页界面：代码对比和抄袭管理分离显示")
    print("✓ 导出按钮：历史记录区域提供导出功能")

def main():
    """主演示函数"""
    print("Python代码查重工具 - 新功能演示")
    print("=" * 50)
    
    try:
        # 演示各个功能
        demo_history_features()
        demo_plagiarism_management()
        demo_export_features()
        demo_gui_features()
        
        print("\n" + "=" * 50)
        print("✓ 所有功能演示完成！")
        print("\n要体验完整功能，请运行: python main.py")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
    
    # 清理演示文件
    try:
        if Path("demo_history.json").exists():
            Path("demo_history.json").unlink()
        if Path("demo_plagiarism_report.json").exists():
            Path("demo_plagiarism_report.json").unlink()
    except:
        pass

if __name__ == "__main__":
    main() 