from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QIcon, QPixmap, QImage
from PyQt5.QtCore import QSize
import fitz

class ReorderPagesDialog(QDialog):
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.setModal(True)
        self.setWindowTitle("Reorder PDF Pages")
        self.layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setIconSize(QSize(150, 210))  # Adjust this size as needed

        self.layout.addWidget(self.list_widget)

        self.load_pdf_thumbnails()

        # Buttons for additional control (optional based on your UI/UX preference)
        btn_layout = QHBoxLayout()
        self.up_btn = QPushButton("Move Up")
        self.down_btn = QPushButton("Move Down")
        self.up_btn.clicked.connect(self.move_up)
        self.down_btn.clicked.connect(self.move_down)
        btn_layout.addWidget(self.up_btn)
        btn_layout.addWidget(self.down_btn)
        self.layout.addLayout(btn_layout)

        # Ok and Cancel buttons
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        self.save_as_btn = QPushButton("Save As")
        self.save_as_btn.clicked.connect(self.save_as)
        btn_layout.addWidget(self.save_as_btn)

        
        self.aboutBtn = QPushButton("How To Use")
        btn_layout.addWidget(self.aboutBtn)
        self.aboutBtn.clicked.connect(self.aboutApp)

    def aboutApp(self):
        QMessageBox.information(self, 'About This Feature', 'Reorder Pages allows for pages to be sorted in any order. Drag-and-Drop or use the buttons to reorder pages.\nFor any feature requests, please tell Billy.')

    def load_pdf_thumbnails(self):
        pdf = fitz.open(self.pdf_path)
        for i, page in enumerate(pdf):
            pix = page.get_pixmap(matrix=fitz.Matrix(1, 1))  # Scale factor to reduce thumbnail size
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(img)
            item = QListWidgetItem(QIcon(pixmap), f"Page {i+1}")
            self.list_widget.addItem(item)
        pdf.close()

    def move_up(self):
        current_row = self.list_widget.currentRow()
        if current_row > 0:
            self.list_widget.insertItem(current_row - 1, self.list_widget.takeItem(current_row))
            self.list_widget.setCurrentRow(current_row - 1)

    def move_down(self):
        current_row = self.list_widget.currentRow()
        if current_row < self.list_widget.count() - 1:
            self.list_widget.insertItem(current_row + 1, self.list_widget.takeItem(current_row))
            self.list_widget.setCurrentRow(current_row + 1)

    def save_as(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Reordered PDF", "", "PDF Files (*.pdf)")
        if save_path:
            if not save_path.endswith('.pdf'):
                save_path += '.pdf'
            self.apply_reordering(save_path)

    def apply_reordering(self, save_path):
        pdf = fitz.open(self.pdf_path)
        new_pdf = fitz.open()
        for row in range(self.list_widget.count()):
            page_text = self.list_widget.item(row).text()
            page_num = int(page_text.split()[1]) - 1  # Extract page number from item text
            new_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)
        pdf.close()
        
        new_pdf.save(save_path)
        new_pdf.close()
        QMessageBox.information(self, 'Success', 'PDF pages reordered and saved successfully.')
