from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import (QMessageBox,QDialog, QListWidget, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog)
from PyQt5.Qt import Qt

class ReorderDialog(QDialog):
    def __init__(self, files, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Merge PDFs')
        self.files = files
        self.setModal(True)
        self.initUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.removeSelectedFiles()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.listWidget = QListWidget(self)
        self.listWidget.setDragDropMode(QListWidget.InternalMove)
        self.listWidget.setSelectionMode(QListWidget.ExtendedSelection)
        for file in self.files:
            self.listWidget.addItem(file)
        self.layout.addWidget(self.listWidget)

        # Add and Remove buttons
        fileBtnLayout = QHBoxLayout()
        self.addBtn = QPushButton('Add File')
        self.removeBtn = QPushButton('Remove Selected')
        fileBtnLayout.addWidget(self.addBtn)
        fileBtnLayout.addWidget(self.removeBtn)
        self.layout.addLayout(fileBtnLayout)

        # Buttons for moving items
        moveBtnLayout = QHBoxLayout()
        self.upBtn = QPushButton('Move Up')
        self.downBtn = QPushButton('Move Down')
        moveBtnLayout.addWidget(self.upBtn)
        moveBtnLayout.addWidget(self.downBtn)
        self.layout.addLayout(moveBtnLayout)

        # Connect signals
        self.addBtn.clicked.connect(self.addFile)
        self.removeBtn.clicked.connect(self.removeSelectedFiles)
        self.upBtn.clicked.connect(self.moveUp)
        self.downBtn.clicked.connect(self.moveDown)


        # Ok and Cancel buttons
        controlBtnLayout = QHBoxLayout()
        okBtn = QPushButton('OK')
        cancelBtn = QPushButton('Cancel')
        controlBtnLayout.addWidget(okBtn)
        controlBtnLayout.addWidget(cancelBtn)
        self.layout.addLayout(controlBtnLayout)
        okBtn.clicked.connect(self.accept)
        cancelBtn.clicked.connect(self.reject)

        # About Button
        aboutBtnLayout = QHBoxLayout()
        aboutBtn = QPushButton("How To Use")
        aboutBtnLayout.addWidget(aboutBtn)
        self.layout.addLayout(aboutBtnLayout)
        aboutBtn.clicked.connect(self.aboutApp)

    def aboutApp(self):
        QMessageBox.information(self, 'About This Feature', 'Merge PDF allows for combining PDFs together in any order desired. Drag-and-Drop or use the buttons to reorder PDFs.\nFor any feature requests, please tell Billy.')

    def addFile(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Add PDF files', '', 'PDF Files (*.pdf)')
        for file in files:
            if file:  
                self.listWidget.addItem(file)
                self.files.append(file)

    def removeSelectedFiles(self):
        for selectedItem in self.listWidget.selectedItems():
            row = self.listWidget.row(selectedItem)
            self.listWidget.takeItem(row)
            self.files.remove(selectedItem.text())

    def moveUp(self):
        currentRow = self.listWidget.currentRow()
        if currentRow >= 1:
            currentItem = self.listWidget.takeItem(currentRow)
            self.listWidget.insertItem(currentRow - 1, currentItem)
            self.listWidget.setCurrentRow(currentRow - 1)

    def moveDown(self):
        currentRow = self.listWidget.currentRow()
        if currentRow < self.listWidget.count() - 1:
            currentItem = self.listWidget.takeItem(currentRow)
            self.listWidget.insertItem(currentRow + 1, currentItem)
            self.listWidget.setCurrentRow(currentRow + 1)

    def getOrderedFiles(self):
        return [self.listWidget.item(i).text() for i in range(self.listWidget.count())]
