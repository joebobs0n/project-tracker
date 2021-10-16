#!/usr/bin/python3

r'''
# Project Tracker Main File
- Author: Monk, Andy
- Email: czech.monk90@gmail.com
'''

from PyQt5 import QtWidgets
from src.mainApp import PTApp
from pathlib import Path
import sys, os
import qdarkstyle


def main():
    version = '1.0.2'

    app = QtWidgets.QApplication([])
    with open('src/stylesheet.scss', 'r') as f:
        css = f.read()
    # app.setStyleSheet(css)
    win = PTApp()
    win.setVersion(version)
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    main()
