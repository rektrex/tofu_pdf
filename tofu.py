#!/usr/bin/env python3

import sys, fitz
import os
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QWidgetItem, QDesktopWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

home = str(Path.home()) # gets $HOME or equivalent

class Tofu(QWidget):
    """Derived from QWidget; is the main widget of the application.

    Parameters:
        filename (string): name of the pdf file to open.

    Returns:
        Tofu: An instance of class Tofu.
    """

    def __init__(self, filename):
        '''Initialize non-UI components, and call initUI.'''

        super().__init__()

        # create '$HOME/.tofu_pdf' if not found
        if not os.path.isdir(home + '/.tofu_pdf'):
            os.mkdir(home + '/.tofu_pdf')

        # define keymaps
        self.keymaps = {
                'j': self.next_page,
                'k': self.previous_page,
                'q': self.quit,
        }

        self.title = os.path.splitext(os.path.basename(filename))[0] # get name of the file, preferred because metadata['title'] is not often available
        self.doc = fitz.open(filename) # open the given file
        self.metadata = self.doc.metadata
        self.pageNumber = 0

        # retrieve data stored about a file
        if os.path.isfile(home + '/.tofu_pdf/' + self.title):
            with open(home + '/.tofu_pdf/' + self.title, 'r') as f:
                oldData = f.read()
                storedData = dict()
                if isinstance(eval(oldData), dict):
                    storedData = eval(oldData)
                    self.pageNumber = storedData.get('pageNumber', 0)

        self.initUI()

    def initUI(self):
        '''Initialize UI components, and call renderPage.'''
         
        # Center window on screen, not accurate right now. TODO fix this
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
        '''Remove label from the layout.'''

        self.vbox.removeItem(self.vbox.itemAt(0))
        self.update()

    def renderPage(self):
        '''Load and render current page from the file.'''

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
        """Save data about the current file.

        Parameters:
            key (string): key/name of the property.
            value (any): value of the property.
        """

        with open(home + '/.tofu_pdf/' + self.title, 'w+') as f:
            oldData = f.read()
            storedData = dict()
            if isinstance(oldData, dict):
                storedData = eval(oldData)
            storedData[key] = value
            f.write(str(storedData))

    def next_page(self):
        '''Move to the next page, moves to the first page if at the last page.'''

        self.pageNumber += 1
        self.renderPage()

    def previous_page(self):
        '''Move to the previous page, moves to the last page if at the first page.'''

        self.pageNumber -= 1
        self.renderPage()

    def quit(self):
        '''Store current page number and quit.'''

        self.saveToFile("pageNumber", self.pageNumber)
        QApplication.instance().quit()

    def keyPressEvent(self, event):
        '''Call functions associated with a key press, if any.'''

        key = event.text()
        if key in self.keymaps.keys():
            self.keymaps[key]()

if __name__ == '__main__':
    filename = sys.argv[1]

    app = QApplication(sys.argv)
    tofu = Tofu(filename)

    sys.exit(app.exec_())
