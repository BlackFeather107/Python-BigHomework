# view/dialog_view.py

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QCheckBox, 
                             QDialogButtonBox, QWidget, QHBoxLayout)
from PyQt5.QtCore import Qt

class AutoMarkDialog(QDialog):
    """自动标记提醒对话框"""
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setWindowTitle("检测到可疑代码")
        self.setModal(True)
        self.setMinimumWidth(350)

        layout = QVBoxLayout(self)
        
        # 内容文本
        content_text = (
            "检测到综合可疑度超过阈值的代码对，已为您自动标记为“抄袭”。\n\n"
            "自动标记结果仅供参考，强烈建议您结合代码详情进行人工核对与分辨。"
        )
        content_label = QLabel(content_text)
        content_label.setWordWrap(True)
        layout.addWidget(content_label)
        
        layout.addSpacing(15)

        # 勾选项
        self.no_auto_mark_checkbox = QCheckBox("取消自动标记")
        self.no_auto_mark_checkbox.setWhatsThis("如果您勾选此项，在您下次登录前，程序将不会再自动标记任何可疑代码，但本次标记仍保留。")
        self.no_show_popup_checkbox = QCheckBox("不再弹窗提醒")
        self.no_show_popup_checkbox.setWhatsThis("如果您勾选此项，在您下次登录前，即使有代码被自动标记，此提示框也不会再弹出。")

        layout.addWidget(self.no_auto_mark_checkbox)
        layout.addWidget(self.no_show_popup_checkbox)

        # 按钮
        # PyQt的标准对话框右上角自带关闭按钮 (X)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

    def get_settings(self) -> dict:
        """获取用户的设置"""
        return {
            'stop_auto_marking': self.no_auto_mark_checkbox.isChecked(),
            'stop_showing_popup': self.no_show_popup_checkbox.isChecked()
        }
