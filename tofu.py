#!/usr/bin/env python3

import sys, fitz
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout, QWidgetItem, QDesktopWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt


home = Path.home() # gets $HOME or equivalent
commands = []

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
        if not (home / '.tofu_pdf').exists():
            (home / '.tofu_pdf').mkdir(parents = True, exist_ok = True)

        # define keymaps
        self.keymaps = {
                'j': self.next_page,
                'k': self.previous_page,
                'q': self.quit,
                'g': self.goto,
        }

        self.title = Path(filename).stem # get name of the file, preferred because metadata['title'] is not often available
        self.doc = fitz.open(filename) # open the given file
        self.metadata = self.doc.metadata
        self.pageNumber = 0

        # retrieve data stored about a file
        self.fileDataPath = home / '.tofu_pdf' / self.title
        if self.fileDataPath.exists():
            oldData = self.fileDataPath.read_text()
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

        storedData = dict()

        if self.fileDataPath.exists():
            oldData = self.fileDataPath.read_text()
            if isinstance(eval(oldData), dict):
                storedData = eval(oldData)

        storedData[key] = value
        self.fileDataPath.write_text(str(storedData))


    def next_page(self):
        '''Move to the next page, moves to the first page if at the last page.'''

        self.pageNumber += 1
        self.renderPage()


    def previous_page(self):
        '''Move to the previous page, moves to the last page if at the first page.'''

        self.pageNumber -= 1
        self.renderPage()


    def goto(self, number):
        """Move to the given page number.

        Parameters:
            number (int): page number to move to.
        """

        self.pageNumber = number
        self.renderPage()


    def quit(self):
        '''Store current page number and quit.'''

        self.saveToFile("pageNumber", self.pageNumber)
        QApplication.instance().quit()


    def keyPressEvent(self, event):
        '''Call functions associated with a key press, if any.'''

        global commands
        key = event.text()

        if key == 'g' or key.isnumeric():
            commands.append(key)
            return

        if event.key() == Qt.Key_Return and commands:
            command = commands[0]
            number = int("".join(commands[1:]))
            commands = []
            self.keymaps[command](number)
            return

        if key in self.keymaps.keys():
            self.keymaps[key]()


if __name__ == '__main__':
    filename = sys.argv[1]

    app = QApplication(sys.argv)
    tofu = Tofu(filename)

    sys.exit(app.exec_())
