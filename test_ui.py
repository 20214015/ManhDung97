#!/usr/bin/env python3
"""
Test UI script để kiểm tra vấn đề hiển thị tab
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test UI - Tab Display")
        self.resize(800, 600)
        
        # Tạo central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Tạo sidebar
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("QFrame#sidebar { background-color: #2D2A2E; }")
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(8)
        
        # Tạo các nút tab
        tabs = [
            ("Dashboard", 0),
            ("Apps", 1), 
            ("Tools", 2),
            ("Scripts", 3),
            ("Cleanup", 4)
        ]
        
        self.tab_buttons = []
        for name, index in tabs:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, i=index: self.switch_tab(i))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #49483E;
                    color: #F8F8F2;
                    border: none;
                    padding: 10px;
                    text-align: left;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #A6E22E;
                    color: #272822;
                }
            """)
            sidebar_layout.addWidget(btn)
            self.tab_buttons.append(btn)
        
        sidebar_layout.addStretch(1)
        
        # Tạo main content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("QStackedWidget { background-color: #272822; }")
        
        # Tạo các trang
        pages = [
            ("Dashboard", "🏠 Dashboard Page\nChọn Dashboard từ sidebar để xem trang này.\nNếu bạn thấy nội dung này, Dashboard đang hoạt động!"),
            ("Apps", "📱 Apps Management Page\nQuản lý ứng dụng"),
            ("Tools", "🔧 Tools Page\nCông cụ hệ thống"),
            ("Scripts", "📝 Scripts Page\nQuản lý script"),
            ("Cleanup", "🧹 Cleanup Page\nDọn dẹp hệ thống")
        ]
        
        for name, content in pages:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            
            title = QLabel(f"{name} Tab")
            title.setStyleSheet("color: #A6E22E; font-size: 24px; font-weight: bold; margin: 20px;")
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            content_label = QLabel(content)
            content_label.setStyleSheet("color: #F8F8F2; font-size: 14px; margin: 20px;")
            content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            content_label.setWordWrap(True)
            
            page_layout.addWidget(title)
            page_layout.addWidget(content_label)
            page_layout.addStretch(1)
            
            self.content_stack.addWidget(page)
        
        # Thêm widgets vào layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack)
        
        # Hiển thị Dashboard (index 0) ban đầu
        self.content_stack.setCurrentIndex(0)
        print(f"Initial tab: {self.content_stack.currentIndex()}")
        print(f"Content stack count: {self.content_stack.count()}")
        
    def switch_tab(self, index):
        print(f"Switching to tab {index}")
        self.content_stack.setCurrentIndex(index)
        print(f"Current index now: {self.content_stack.currentIndex()}")
        
        # Kiểm tra widget hiện tại
        current_widget = self.content_stack.currentWidget()
        print(f"Current widget: {type(current_widget)}")
        print(f"Widget visible: {current_widget.isVisible() if current_widget else 'None'}")
        print(f"Widget size: {current_widget.size() if current_widget else 'None'}")

def main():
    app = QApplication(sys.argv)
    
    window = TestMainWindow()
    window.show()
    
    print("Test window created and shown")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
