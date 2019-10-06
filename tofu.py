#!/usr/bin/env python3

import sys, fitz
import os
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QWidgetItem, QDesktopWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

home = str(Path.home())

class Tofu(QWidget):

    def __init__(self, filename):
        super().__init__()

        if not os.path.isdir(home + '/.tofu_pdf'):
            os.mkdir(home + '/.tofu_pdf')

        self.keymaps = {
                'j': self.next_page,
                'k': self.previous_page,
                'q': self.quit,
        }

        self.title = os.path.splitext(os.path.basename(filename))[0]
        self.doc = fitz.open(filename)
        self.metadata = self.doc.metadata
        self.pageNumber = 0

        with open(home + '/.tofu_pdf/' + self.title, 'r') as f:
            oldData = f.read()
            storedData = dict()
            if isinstance(eval(oldData), dict):
                storedData = eval(oldData)
                self.pageNumber = storedData.get('pageNumber', 0)

        self.initUI()

    def initUI(self):
        # Center window on screen, not accurate right now
        qtRect = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRect.moveCenter(centerPoint)
        self.move(qtRect.topLeft())

        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)
        self.setWindowTitle('Tofu PDF')
        self.show()
        self.renderPage()

    def clearLayout(self):
        self.vbox.removeItem(self.vbox.itemAt(0))
        self.update()

    def renderPage(self):
        self.clearLayout()
        page = self.doc[self.pageNumber]
        pix = page.getPixmap()
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        pixmap = QPixmap.fromImage(img)

        label = QLabel(self)
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)
        
        self.vbox.addWidget(label)
        self.vbox.setContentsMargins(0, 0, 0, 0)

        self.update()

    def saveToFile(self, key, value):
        with open(home + '/.tofu_pdf/' + self.title, 'w+') as f:
            oldData = f.read()
            storedData = dict()
            if isinstance(oldData, dict):
                storedData = eval(oldData)
            storedData[key] = value
            f.write(str(storedData))

    def next_page(self):
        self.pageNumber += 1
        self.renderPage()

    def previous_page(self):
        self.pageNumber -= 1
        self.renderPage()

    def quit(self):
        self.saveToFile("pageNumber", self.pageNumber)
        QApplication.instance().quit()

    def keyPressEvent(self, event):
        key = event.text()
        if key in self.keymaps.keys():
            self.keymaps[key]()

if __name__ == '__main__':
    filename = sys.argv[1]

    app = QApplication(sys.argv)
    tofu = Tofu(filename)

    sys.exit(app.exec_())
