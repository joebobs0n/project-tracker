#!/usr/bin/python3

r'''
# Project Tracker Main File
- Author: Monk, Andy
- Email: czech.monk90@gmail.com
'''

import sys, shutil, os
from PyQt5 import QtWidgets
from src.sibylMain import SibylMain
from src.autoUpdate import Updater
import src.literals as literals
from src.helpers import getRoot


def main():
    app = QtWidgets.QApplication([])
    if Updater.checkLatest(literals.gh_repo, literals.gh_token):
        root = getRoot(True)
        if not (root / 'installer').exists():
            os.mkdir(str(root / 'installer'))
        for item in literals.installer_cleanup:
            if (root / item).exists():
                shutil.move(str(root / item), str(root / 'installer' / item))

        win = SibylMain()
        win.show()
        sys.exit(app.exec_())
    else:
        app.quit()
        sys.exit()

if __name__ == '__main__':
    main()
