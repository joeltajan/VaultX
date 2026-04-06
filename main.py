import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QLineEdit, QFileDialog, 
                             QMessageBox, QStackedWidget, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog, QTextEdit, 
                             QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
import fitz  # PyMuPDF
from vault_manager import VaultManager

QSS_THEME = """
QWidget {
    background-color: #000000;
    color: #00E5FF;
    font-family: 'Consolas', 'Courier New', monospace;
}
QLineEdit {
    background-color: #000000;
    border: 1px solid #333333;
    padding: 8px;
    font-size: 14px;
}
QLineEdit:focus {
    border: 1px solid #00E5FF;
}
QLabel#header {
    font-size: 16px;
    font-weight: bold;
    color: #00E5FF;
}
QLabel#subtext {
    color: #888888;
    font-size: 14px;
}
QPushButton {
    background-color: #0A0A0A;
    color: #00E5FF;
    border: 1px solid #333333;
    padding: 12px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #111111;
    border: 1px solid #00E5FF;
}
QPushButton:pressed {
    background-color: #00E5FF;
    color: #000000;
}
QPushButton#deleteBtn {
    color: #FF3333;
    border: 1px solid #880000;
    background-color: #220000;
}
QPushButton#deleteBtn:hover {
    background-color: #440000;
    border: 1px solid #FF3333;
}
QPushButton#deleteBtn:pressed {
    background-color: #FF3333;
    color: #000000;
}
QPushButton#lockBtn {
    color: #777777;
    background-color: #0A0A0A;
}
QTableWidget {
    background-color: #000000;
    border: 1px solid #DDDDDD;
    gridline-color: #111111;
    selection-background-color: #00E5FF;
    selection-color: #000000;
    font-size: 14px;
    outline: 0;
}
QTableWidget::item {
    padding: 5px;
}
QHeaderView::section {
    background-color: #0A0A0A;
    color: #00E5FF;
    border: none;
    border-bottom: 1px solid #333333;
    padding: 6px;
}
"""

class PreviewDialog(QDialog):
    def __init__(self, filename, content, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"VIEWER // {filename}")
        self.setFixedSize(600, 700)
        self.setStyleSheet(QSS_THEME + "QTextEdit {background: black; border: 1px solid #333333; color: #00E5FF;}")
        
        self.current_pdf_doc = None
        self.current_pdf_page = 0
        
        layout = QVBoxLayout(self)
        
        self.preview_label = QLabel("LOADING...")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.hide()
        
        self.nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("<<<")
        self.next_btn = QPushButton(">>>")
        self.page_label = QLabel("PG 1 / _")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.prev_btn.clicked.connect(self.prev_pdf_page)
        self.next_btn.clicked.connect(self.next_pdf_page)
        
        self.nav_layout.addWidget(self.prev_btn)
        self.nav_layout.addWidget(self.page_label)
        self.nav_layout.addWidget(self.next_btn)
        
        self.pdf_nav_widget = QWidget()
        self.pdf_nav_widget.setLayout(self.nav_layout)
        self.pdf_nav_widget.hide()
        
        layout.addWidget(self.preview_label, stretch=1)
        layout.addWidget(self.preview_text, stretch=1)
        layout.addWidget(self.pdf_nav_widget)
        
        self.load_content(filename, content)

    def load_content(self, filename, content):
        ext = os.path.splitext(filename)[1].lower()
        self.preview_label.hide()
        self.preview_text.hide()
        self.pdf_nav_widget.hide()
        self.preview_label.clear()
        
        image_exts = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
        text_exts = ['.txt', '.md', '.csv', '.json', '.xml', '.py', '.js', '.html', '.css', '.ini']
        
        if ext in image_exts:
            pixmap = QPixmap()
            pixmap.loadFromData(content)
            
            w, h = 560, 660
            scaled_pixmap = pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_label.show()
            
        elif ext in text_exts:
            try:
                text = content.decode('utf-8')
                self.preview_text.setPlainText(text)
                self.preview_text.show()
            except UnicodeDecodeError:
                self.preview_label.setText("ERR: ENCODING NOT SUPPORTED.")
                self.preview_label.show()
                
        elif ext == '.pdf':
            try:
                self.current_pdf_doc = fitz.open(stream=content, filetype="pdf")
                self.current_pdf_page = 0
                self.render_pdf_page()
            except Exception as e:
                self.preview_label.setText("ERR: RENDER LAYER FAULT.")
                self.preview_label.show()
        else:
            self.preview_label.setText(f"ERR: {ext.upper()} FORMAT NOT SUPPORTED.\nPLEASE EXTRACT.")
            self.preview_label.show()
            
    def render_pdf_page(self):
        if not self.current_pdf_doc: return
        page = self.current_pdf_doc.load_page(self.current_pdf_page)
        pix = page.get_pixmap()
        fmt = QImage.Format.Format_RGBA8888 if pix.alpha else QImage.Format.Format_RGB888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        pixmap = QPixmap.fromImage(img)
        scaled_pixmap = pixmap.scaled(560, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.preview_label.setPixmap(scaled_pixmap)
        self.preview_label.show()
        self.page_label.setText(f"PG {self.current_pdf_page + 1} / {self.current_pdf_doc.page_count}")
        self.pdf_nav_widget.show()
        
    def prev_pdf_page(self):
        if self.current_pdf_doc and self.current_pdf_page > 0:
            self.current_pdf_page -= 1
            self.render_pdf_page()
            
    def next_pdf_page(self):
        if self.current_pdf_doc and self.current_pdf_page < self.current_pdf_doc.page_count - 1:
            self.current_pdf_page += 1
            self.render_pdf_page()

    def closeEvent(self, event):
        if self.current_pdf_doc:
            self.current_pdf_doc.close()
            self.current_pdf_doc = None
        super().closeEvent(event)

class VaultXApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MANIFEST // PROTOCOL")
        self.setFixedSize(800, 600)
        
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.vault_file = os.path.join(base_dir, 'sys_data.vault')
        self.vault = VaultManager(self.vault_file)
        
        self.init_ui()

    def init_ui(self):
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.login_screen = self.build_login_screen()
        self.dashboard_screen = self.build_dashboard_screen()
        
        self.stacked_widget.addWidget(self.login_screen)
        self.stacked_widget.addWidget(self.dashboard_screen)

    def build_login_screen(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("ØØ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("INPUT DECRYPTION KEY_")
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setFixedWidth(300)
        self.pwd_input.returnPressed.connect(self.handle_login)
        
        btn_text = "INITIALIZE CONNECTION" if self.vault.is_initialized() else "FORMAT ENCLAVE"
        self.login_btn = QPushButton(btn_text)
        self.login_btn.setFixedWidth(300)
        self.login_btn.clicked.connect(self.handle_login)
        
        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.pwd_input, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        return widget

    def build_dashboard_screen(self):
        widget = QWidget()
        main_layout = QHBoxLayout(widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(25)
        
        # Left Side: Manifest Table
        left_layout = QVBoxLayout()
        
        left_top_layout = QHBoxLayout()
        lbl_manifest = QLabel("MANIFEST")
        lbl_manifest.setObjectName("header")
        
        self.lbl_total = QLabel("TOTAL: 0.00")
        self.lbl_total.setObjectName("subtext")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        left_top_layout.addWidget(lbl_manifest)
        left_top_layout.addWidget(self.lbl_total)
        
        self.file_table = QTableWidget(0, 2)
        self.file_table.setHorizontalHeaderLabels(["FILE NAME", "SIZE"])
        self.file_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.file_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.file_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setShowGrid(False)
        self.file_table.itemDoubleClicked.connect(self.preview_selected)
        
        self.lbl_status = QLabel("STATUS: IDLE")
        self.lbl_status.setObjectName("subtext")
        
        left_layout.addLayout(left_top_layout)
        left_layout.addWidget(self.file_table)
        left_layout.addWidget(self.lbl_status)
        
        # Right Side: Actions
        right_layout = QVBoxLayout()
        
        lbl_actions = QLabel("ACTIONS")
        lbl_actions.setObjectName("header")
        lbl_actions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        open_btn = QPushButton("OPEN")
        open_btn.clicked.connect(self.preview_selected)
        
        import_btn = QPushButton("IMPORT")
        import_btn.clicked.connect(self.import_file)
        
        export_btn = QPushButton("EXPORT")
        export_btn.clicked.connect(self.export_file)
        
        delete_btn = QPushButton("DELETE")
        delete_btn.setObjectName("deleteBtn")
        delete_btn.clicked.connect(self.delete_file)
        
        lock_btn = QPushButton("LOCK")
        lock_btn.setObjectName("lockBtn")
        lock_btn.clicked.connect(self.lock_vault)
        
        right_layout.addWidget(lbl_actions)
        right_layout.addSpacing(10)
        right_layout.addWidget(open_btn)
        right_layout.addWidget(import_btn)
        right_layout.addWidget(export_btn)
        right_layout.addSpacing(10)
        right_layout.addWidget(delete_btn)
        right_layout.addStretch()
        right_layout.addWidget(lock_btn)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        right_widget.setFixedWidth(180)
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)
        
        return widget

    def set_status(self, text):
        self.lbl_status.setText(f"STATUS: {text}")

    def get_selected_filename(self):
        rows = self.file_table.selectedItems()
        if not rows: return None
        return self.file_table.item(rows[0].row(), 0).text()

    def handle_login(self):
        pwd = self.pwd_input.text()
        if not pwd:
            QMessageBox.warning(self, "SYS_ERR", "KEY CANNOT BE NULL.")
            return
        
        self.set_status("DECRYPTING...")    
        try:
            if self.vault.is_initialized():
                self.vault.load_vault(pwd)
            else:
                self.vault.initialize_new(pwd)
                QMessageBox.information(self, "SYS_OK", "ENCLAVE FORMATTED.\n\nNO RECOVERY MECHANISM EXISTS.")
            
            self.pwd_input.clear()
            self.refresh_file_list()
            self.stacked_widget.setCurrentWidget(self.dashboard_screen)
            self.set_status("IDLE")
            
        except ValueError as e:
            QMessageBox.critical(self, "AUTH_FAIL", str(e).upper())
            self.set_status("AUTH_FAIL")

    def refresh_file_list(self):
        self.file_table.setRowCount(0)
        files = self.vault.list_files()
        total_size = 0
        
        for i, (name, size, mod_time) in enumerate(files):
            total_size += size
            self.file_table.insertRow(i)
            
            if size >= (1024 * 1024):
                size_str = f"{size / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{size / 1024:.2f} KB"
                
            self.file_table.setItem(i, 0, QTableWidgetItem(name))
            self.file_table.setItem(i, 1, QTableWidgetItem(size_str))
            
        if total_size >= (1024 * 1024):
            self.lbl_total.setText(f"TOTAL: {total_size / (1024 * 1024):.2f} MB")
        else:
            self.lbl_total.setText(f"TOTAL: {total_size / 1024:.2f} KB")

    def import_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "SELECT FILES FOR INGESTION")
        if files:
            self.set_status("INGESTING DATA...")
            for f in files:
                try:
                    self.vault.add_file(f)
                except Exception:
                    pass
            self.refresh_file_list()
            self.set_status("IDLE")

    def export_file(self):
        filename = self.get_selected_filename()
        if not filename: return
            
        dest, _ = QFileDialog.getSaveFileName(self, "TARGET DESTINATION", filename)
        if dest:
            self.set_status("EXTRACTING...")
            try:
                self.vault.export_file(filename, dest)
            except Exception:
                pass
            self.set_status("IDLE")

    def delete_file(self):
        filename = self.get_selected_filename()
        if not filename: return
        
        confirm = QMessageBox.question(self, "CONFIRM_PURGE", f"PERMANENTLY PURGE '{filename}'?", 
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            self.set_status("PURGING DATA...")
            self.vault.remove_file(filename)
            self.refresh_file_list()
            self.set_status("IDLE")

    def preview_selected(self):
        filename = self.get_selected_filename()
        if not filename: return
            
        self.set_status("LOADING VIEWER...")
        content = self.vault.get_file_content(filename)
        if content:
            viewer = PreviewDialog(filename, content, self)
            viewer.exec()
        self.set_status("IDLE")

    def lock_vault(self):
        self.set_status("SECURING ENCLAVE...")
        self.vault.data = {"files": {}}
        self.vault.password = None
        self.file_table.setRowCount(0)
        self.login_btn.setText("INITIALIZE CONNECTION" if self.vault.is_initialized() else "FORMAT ENCLAVE")
        self.stacked_widget.setCurrentWidget(self.login_screen)
        self.set_status("IDLE")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS_THEME)
    window = VaultXApp()
    window.show()
    sys.exit(app.exec())
