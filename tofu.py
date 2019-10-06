#!/usr/bin/env python3

import sys, fitz
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QWidgetItem, QDesktopWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class Tofu(QWidget):

    def __init__(self, filename):
        super().__init__()

        self.keymaps = {
                'j': self.next_page,
                'k': self.previous_page,
                'q': self.quit,
        }

        self.doc = fitz.open(filename)
        self.pageNumber = 0
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

    def closeEvent(self, event):
        pass

    def next_page(self):
        self.pageNumber += 1
        self.renderPage()

    def previous_page(self):
        self.pageNumber -= 1
        self.renderPage()

    def quit(self):
        QApplication.instance().quit()

    def keyPressEvent(self, event):
        key = event.text()
        if key in self.keymaps.keys():
            self.keymaps[key]()

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
