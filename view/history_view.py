# view/history_view.py

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QLabel, QDialog,
                             QTextEdit, QDialogButtonBox, QMessageBox,
                             QFileDialog, QGroupBox, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from datetime import datetime
from pathlib import Path

class PlagiarismMarkDialog(QDialog):
    """抄袭标记对话框"""
    def __init__(self, file_a: str, file_b: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("标记抄袭状态")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 文件信息
        info_label = QLabel(f"文件A: {Path(file_a).name}\n文件B: {Path(file_b).name}")
        layout.addWidget(info_label)
        
        # 抄袭状态选择
        self.plagiarism_checkbox = QCheckBox("标记为抄袭")
        layout.addWidget(self.plagiarism_checkbox)
        
        # 备注输入
        notes_label = QLabel("备注:")
        layout.addWidget(notes_label)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        layout.addWidget(self.notes_edit)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_result(self):
        """获取对话框结果"""
        return {
            'is_plagiarism': self.plagiarism_checkbox.isChecked(),
            'notes': self.notes_edit.toPlainText()
        }

class HistoryView(QWidget):
    """历史记录视图"""
    session_selected = pyqtSignal(str)  # 发送会话ID
    plagiarism_marked = pyqtSignal(str, str, bool, str)  # 文件A, 文件B, 是否抄袭, 备注
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("历史记录")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 登录时间显示
        login_time = self.controller.get_login_time()
        login_label = QLabel(f"登录时间: {login_time.strftime('%Y-%m-%d %H:%M:%S')}")
        layout.addWidget(login_label)
        
        # 历史会话列表
        self.session_list = QListWidget()
        self.session_list.itemDoubleClicked.connect(self.on_session_selected)
        layout.addWidget(self.session_list)
        
        # 按钮组
        button_layout_above = QHBoxLayout()
        button_layout_behind = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_sessions)
        button_layout_above.addWidget(self.refresh_btn)

        self.clear_btn = QPushButton("清除")
        self.clear_btn.clicked.connect(self.clear_history)
        button_layout_above.addWidget(self.clear_btn)
        
        self.export_report_btn = QPushButton("导出抄袭报告")
        self.export_report_btn.clicked.connect(self.export_plagiarism_report)
        button_layout_behind.addWidget(self.export_report_btn)
        
        self.export_files_btn = QPushButton("导出抄袭文件")
        self.export_files_btn.clicked.connect(self.export_plagiarism_files)
        button_layout_behind.addWidget(self.export_files_btn)
        
        layout.addLayout(button_layout_above)
        layout.addLayout(button_layout_behind)
        
        # 初始加载
        self.refresh_sessions()
    
    def refresh_sessions(self):
        """刷新历史会话列表"""
        self.session_list.clear()
        sessions = self.controller.get_all_sessions()
        
        for session in sessions:
            # 创建会话项
            session_text = f"{session.analysis_time.strftime('%Y-%m-%d %H:%M')} - {Path(session.directory).name}"
            if session.get_plagiarism_results():
                session_text += " [包含抄袭判定]"
            
            item = QListWidgetItem(session_text)
            item.setData(Qt.UserRole, session.session_id)
            self.session_list.addItem(item)
    
    def clear_history(self):
        """清除历史会话列表"""
        self.session_list.clear()
        self.controller.clear_all_histories()

    def on_session_selected(self, item):
        """会话被选中"""
        session_id = item.data(Qt.UserRole)
        self.session_selected.emit(session_id)
    
    def export_plagiarism_report(self):
        """导出抄袭报告"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存抄袭报告", 
            f"plagiarism_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            if self.controller.export_plagiarism_report(file_path):
                QMessageBox.information(self, "成功", "抄袭报告导出成功！")
            else:
                QMessageBox.warning(self, "错误", "抄袭报告导出失败！")
    
    def export_plagiarism_files(self):
        """导出抄袭文件"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择导出目录")
        
        if dir_path:
            if self.controller.export_plagiarism_files(dir_path):
                QMessageBox.information(self, "成功", "抄袭文件导出成功！")
            else:
                QMessageBox.warning(self, "错误", "抄袭文件导出失败！")

class PlagiarismManagementView(QWidget):
    """抄袭管理视图"""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("抄袭管理")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 抄袭会话列表
        self.plagiarism_list = QListWidget()
        self.plagiarism_list.itemDoubleClicked.connect(self.on_plagiarism_item_selected)
        layout.addWidget(self.plagiarism_list)
        
        # 刷新按钮
        self.refresh_btn = QPushButton("刷新抄袭记录")
        self.refresh_btn.clicked.connect(self.refresh_plagiarism_sessions)
        layout.addWidget(self.refresh_btn)
        
        # 初始加载
        self.refresh_plagiarism_sessions()
    
    def refresh_plagiarism_sessions(self):
        """刷新抄袭会话列表"""
        self.plagiarism_list.clear()
        sessions = self.controller.get_plagiarism_sessions()
        
        for session in sessions:
            for result in session.get_plagiarism_results():
                item_text = f"{session.analysis_time.strftime('%Y-%m-%d %H:%M')} - {Path(result.file_a).name} vs {Path(result.file_b).name}"
                if result.plagiarism_notes:
                    item_text += f" (备注: {result.plagiarism_notes[:20]}...)"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, {
                    'session_id': session.session_id,
                    'file_a': result.file_a,
                    'file_b': result.file_b
                })
                self.plagiarism_list.addItem(item)
    
    def on_plagiarism_item_selected(self, item):
        """抄袭项被选中"""
        data = item.data(Qt.UserRole)
        # 这里可以显示详细的抄袭信息或编辑抄袭状态
        pass 