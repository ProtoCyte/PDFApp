from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, QMessageBox)

class SplitPDFDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Split PDF into Multiple Files')
        self.setModal(True)
        layout = QVBoxLayout(self)
        
        instructions_label = QLabel("Add rows for each split. Specify start page, end page, and file name.")
        layout.addWidget(instructions_label)
        
        self.splits_table = QTableWidget(0, 3)  # 3 columns for start page, end page, and file name
        self.splits_table.setHorizontalHeaderLabels(["Start Page", "End Page", "File Name"])
        self.splits_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.splits_table)
        
        buttons_layout = QHBoxLayout()
        add_row_button = QPushButton("Add Row")
        add_row_button.clicked.connect(self.add_row)
        buttons_layout.addWidget(add_row_button)
        
        remove_row_button = QPushButton("Remove Selected Row")
        remove_row_button.clicked.connect(self.remove_selected_row)
        buttons_layout.addWidget(remove_row_button)
        
        layout.addLayout(buttons_layout)
        
        split_button = QPushButton("Split PDF")
        split_button.clicked.connect(self.on_split_clicked)
        layout.addWidget(split_button)

        aboutBtn = QPushButton("How To Use")
        layout.addWidget(aboutBtn)
        aboutBtn.clicked.connect(self.aboutApp)

        self.add_row()
    
    def aboutApp(self):
        QMessageBox.information(self, 'About This Feature', 'Split PDF allows for splitting the open PDF into smaller PDFs with inputted page range.\nFor any feature requests, please tell Billy.')
    
    def add_row(self):
        self.splits_table.insertRow(self.splits_table.rowCount())
    
    def remove_selected_row(self):
        for index in sorted(self.splits_table.selectionModel().selectedRows(), reverse=True):
            self.splits_table.removeRow(index.row())
    
    def get_inputs(self):
        inputs = []
        for row in range(self.splits_table.rowCount()):
            start_item = self.splits_table.item(row, 0)
            end_item = self.splits_table.item(row, 1)
            file_name_item = self.splits_table.item(row, 2)
            if start_item and end_item and file_name_item and file_name_item.text():
                inputs.append({
                    'start': start_item.text(),
                    'end': end_item.text(),
                    'file_name': file_name_item.text()
                })
            else:
                return None  # Invalid input detected
        return inputs

    def on_split_clicked(self):
        if self.get_inputs() is None:
            QMessageBox.critical(self, 'Error', 'All fields must be filled out, and a file name must be provided for each split.')
        else:
            self.accept()

