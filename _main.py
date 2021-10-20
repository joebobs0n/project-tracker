#!/usr/bin/python3

r'''
# Project Tracker Main File
- Author: Monk, Andy
- Email: czech.monk90@gmail.com
'''

import sys, os
from PyQt5 import QtWidgets
from pathlib import Path
from src.mainApp import PTApp
from src.autoUpdate import Updater
import src.literals as literals


if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    app = QtWidgets.QApplication([])
    isLatest = Updater.checkLatest(literals.gh_repo, literals.gh_token)

    if isLatest:
        win = PTApp()
        win.show()
        sys.exit(app.exec_())
    else:
        app.quit()
        sys.exit()
