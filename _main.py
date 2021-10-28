#!/usr/bin/python3

r'''
# Project Tracker Main File
- Author: Monk, Andy
- Email: czech.monk90@gmail.com
'''

import sys, shutil, os, urllib3, requests, github
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
from src.sibylMain import SibylMain
from src.autoUpdate import Updater
import src.literals as literals
from src.helpers import getRoot


def main():
    app = QtWidgets.QApplication([])
    try:
        isLatest = Updater.checkLatest(literals.gh_repo, literals.gh_token)
    except (urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectTimeout):
        isLatest = 'timeout'
    except github.GithubException:
        isLatest = 'gh_ratelimit'

    if type(isLatest) == str:
        warning = QtWidgets.QMessageBox(
            QtWidgets.QMessageBox.Warning,
            'Latest Check Failed',
            f'Failed to check for newer Sibyl version. Fail code: {isLatest}',
            parent=None
        )
        warning.setWindowIcon(QIcon(str(getRoot(True) / 'icons/dialog.png')))
        warning.exec_()

    if isLatest:
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
