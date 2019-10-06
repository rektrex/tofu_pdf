#!/usr/bin/env python3

import sys, fitz
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QWidgetItem
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class Tofu(QWidget):

    def __init__(self, filename):
        super().__init__()

        self.doc = fitz.open(filename)
        self.pageNumber = 0
        self.initUI()

    def initUI(self):
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)
        self.setWindowTitle('Tofu PDF')
        self.show()
        self.renderPage()

    def renderPage(self, number = 0):
        page = self.doc[number]
        pix = page.getPixmap()
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        pixmap = QPixmap.fromImage(img)

        label = QLabel(self)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        
        self.vbox.addWidget(label)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.pageNumber = number
        self.update()

def openFile(filename):
    doc = fitz.open(filename)
    page = doc[0]
    pix = page.getPixmap()
    fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
    qtimg = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
    return QPixmap.fromImage(qtimg)

if __name__ == '__main__':
    filename = sys.argv[1]

    app = QApplication(sys.argv)
    tofu = Tofu(filename)

    sys.exit(app.exec_())
