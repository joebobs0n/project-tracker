#!/usr/bin/python3

r'''
# Project Tracker Main File
- Author: Monk, Andy
- Email: czech.monk90@gmail.com
'''

import multiprocessing as multi
from PyQt5 import QtWidgets
from src.mainApp import PTApp
from pathlib import Path
import sys, os
# import qdarkstyle

import src.helpers as helpers
from src.magic_numbers import version


if __name__ == '__main__':
    multi.freeze_support()

    os.chdir(Path(__file__).parent)
    app = QtWidgets.QApplication([])
    # helpers.popup('Zombie Count', str(multi.active_children()), QtWidgets.QMessageBox.Critical)
    # latest = helpers.checkLatest()

    # with open('src/stylesheet.scss', 'r') as f:
    #     css = f.read()
    # app.setStyleSheet(css)
    # if latest:
    if True:
        win = PTApp()
        win.show()
    sys.exit(app.exec_())
