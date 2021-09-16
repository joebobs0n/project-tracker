r'''
# Project Tracker Main File
- Author: Monk, Andy
- Email: czech.monk90@gmail.com
- Last Modified: Sept 8, 2021
'''

from PyQt5 import QtWidgets
from src.mainApp import PTApp
import sys
import qdarkstyle


def main():
    app = QtWidgets.QApplication([])
    # print(qdarkstyle.load_stylesheet_pyqt5())
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    win = PTApp()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
