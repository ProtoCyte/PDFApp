import sys
from PyQt5.QtWidgets import (QFileDialog, QTabWidget, QHBoxLayout, QApplication, QMainWindow, QPushButton,
                            QVBoxLayout, QWidget, QLabel, QScrollArea)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QDialog
from mergePDFDialog import ReorderDialog
from splitPDFDialog import SplitPDFDialog
from ReorderPagesDialog import ReorderPagesDialog
import fitz

class PDFReaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main Window Setup
        self.setWindowTitle('PDF Reader')
        self.setGeometry(100, 100, 800, 600)

        # Central Widget and Layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QHBoxLayout(centralWidget)

        # Tab System (Vertical Layout with Buttons)
        button_system = QVBoxLayout()

        open_button = QPushButton('Open PDF')
        open_button.clicked.connect(self.open_pdf)
        button_system.addWidget(open_button)

        # save_button = QPushButton('Save PDF')
        # save_button.clicked.connect(self.save_pdf)
        # button_system.addWidget(save_button)

        # read note by edit_pdf function
        # edit_button = QPushButton('Edit PDF')
        # edit_button.clicked.connect(self.edit_pdf)
        # button_system.addWidget(edit_button)

        merge_button = QPushButton('Merge PDF')
        merge_button.clicked.connect(self.merge_pdf)
        button_system.addWidget(merge_button)

        split_button = QPushButton('Split PDF')
        split_button.clicked.connect(self.split_pdf)
        button_system.addWidget(split_button)

        reorder_button = QPushButton('Reorder Pages')
        reorder_button.clicked.connect(self.reorder_pdf)
        button_system.addWidget(reorder_button)

        about_button = QPushButton('About Application')
        about_button.clicked.connect(self.about_app)
        button_system.addWidget(about_button)

        # Tab Widget for Multiple PDFs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        # Add the tab system and the PDF reader area to the main layout
        layout.addLayout(button_system)
        layout.addWidget(self.tab_widget)
    
    def about_app(self):
        QMessageBox.information(self, 'About This Application', 'This is a small scale PDF application that is able to merge, split and reorder pages in a given PDF. \nFor any questions, please message Billy')

    def add_new_tab(self, pdf_path=None):
        if pdf_path:
            pdf = fitz.open(pdf_path)
            file_path_name = f"{pdf_path}"
            last_slash_index = file_path_name.rfind('/')
            tab_name = file_path_name[last_slash_index + 1:]
            new_tab = QWidget()
            new_tab.pdf_path = pdf_path  # Store the PDF path in the tab's widget
            new_tab.total_pages = len(pdf)  # Store the total number of pages in the tab's widget
            tab_layout = QVBoxLayout(new_tab)

            # Scroll Area for the PDF Viewer
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            tab_layout.addWidget(scroll_area)

            # Container for PDF pages
            pdf_container = QWidget()
            pdf_layout = QVBoxLayout(pdf_container)
            scroll_area.setWidget(pdf_container)

            # Display each page of the PDF
            for page_number in range(len(pdf)):
                page = pdf.load_page(page_number)
                pix = page.get_pixmap()
                qimg = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                img_label = QLabel()
                img_label.setPixmap(QPixmap.fromImage(qimg))
                pdf_layout.addWidget(img_label)

            self.tab_widget.addTab(new_tab, tab_name)

    
    def close_tab(self, index):
        widget = self.tab_widget.widget(index)
        self.cleanup_tab(widget)
        self.tab_widget.removeTab(index)
        widget.deleteLater()

    def cleanup_tab(self, widget):
        if hasattr(widget, 'pdf_document') and widget.pdf_document:
            widget.pdf_document.close()  # Close the document to release resources
            widget.pdf_document = None  # Help the garbage collector by removing the reference

    # Function placeholders for the PDF operations
    def merge_pdf(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select files to merge', '', 'PDF Files (*.pdf)')
        if files:
            # Open the reorder dialog
            dialog = ReorderDialog(files, self)
            if dialog.exec_() == QDialog.Accepted:
                ordered_files = dialog.getOrderedFiles()
                merged_pdf = fitz.open()
                for file_path in ordered_files:
                    doc = fitz.open(file_path)
                    merged_pdf.insert_pdf(doc)
                    doc.close()  # Close the document to release resources
                output_path, _ = QFileDialog.getSaveFileName(self, 'Save merged Files as', '', 'PDF Files (*.pdf)')
                if output_path:
                    merged_pdf.save(output_path)
                    merged_pdf.close()
                    QMessageBox.information(self, 'Success', 'PDFs merged and saved successfully!')
                else:
                    QMessageBox.critical(self, 'Error', 'No output file selected.')
            else:
                QMessageBox.warning(self, 'Cancelled', 'PDF merge cancelled.')
        else:
            QMessageBox.critical(self, 'Error', 'No files selected for merging.')

    def split_pdf(self):
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            QMessageBox.critical(self, 'Error', 'No tab open')
            return
        
        dialog = SplitPDFDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            splits = dialog.get_inputs()
            if splits:
                # Prompt the user to select a directory for saving the split PDFs
                save_directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save Split PDFs")
                if save_directory:
                    self.process_split(current_widget.pdf_path, splits, save_directory)
                else:
                    QMessageBox.warning(self, 'Warning', 'No directory selected. Split operation cancelled.')
            else:
                QMessageBox.critical(self, 'Error', 'Invalid input for splitting PDF.')





    def process_split(self, pdf_path, splits, save_directory):
        doc = fitz.open(pdf_path)
        
        for split in splits:
            start, end, file_name = int(split['start']), int(split['end']), split['file_name']
            
            if start < 1 or end > doc.page_count or start > end:
                QMessageBox.critical(self, 'Error', f'Page range {start}-{end} is out of bounds. The document has {doc.page_count} pages.')
                return
            
            new_doc = fitz.open()
            for page_num in range(start - 1, end):
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
            
            # Construct the full path where the split PDF will be saved
            new_pdf_path = f"{save_directory}/{file_name}.pdf"
            new_doc.save(new_pdf_path)
            new_doc.close()

        doc.close()
        QMessageBox.information(self, 'Success', 'PDF(s) split successfully.')





    def open_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select PDF file to load', '', 'PDF Files (*.pdf)')
        if file_path:
                self.add_new_tab(file_path)
            
        QMessageBox.information(self, 'Success', 'PDF opened in a new tab.')

    # Do save pdf for last cuz it has to save all the edits and stuff.
    def save_pdf(self):
        print('Save PDF functionality goes here.')
    
    # Wayyy too difficult with all the implementations and stuff
    # def edit_pdf(self):
    #     print('Edit PDF functionality goes here.')

    def reorder_pdf(self):
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            QMessageBox.critical(self, 'Error', 'No PDF is currently open.')
            return

        pdf_path = current_widget.pdf_path  # Ensure this attribute is correctly set
        dialog = ReorderPagesDialog(pdf_path, self)
        dialog.exec_()


# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = PDFReaderGUI()
    mainWin.show()
    sys.exit(app.exec_())
