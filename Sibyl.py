#!/usr/bin/python3

r'''
# Project Tracker Main File
- Author: Monk, Andy
- Email: czech.monk90@gmail.com
'''

import sys, shutil, urllib3, requests, github, json, os
from PyQt5.QtGui import QIcon
from PyQt5 import QtWidgets
from src.sibylMain import SibylMain
from src.autoUpdate import Updater
import src.literals as literals
import src.helpers as helpers


def main():
    root = helpers.getRoot(True)
    app = QtWidgets.QApplication([])

    with open(str(root / 'settings.json'), 'r') as f:
        settings = json.load(f)
    gh_token = helpers.retrieve(settings, 'gh_token')

    try:
        isLatest = Updater.checkLatest(literals.gh_repo, gh_token)
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
        warning.setWindowIcon(QIcon(str(root / 'icons/dialog.png')))
        warning.exec_()

    if isLatest:
        if not (root / 'installer').exists():
            os.mkdir(str(root / 'installer'))
        for item in literals.installer_cleanup:
            item_path = root / item
            if item_path.exists():
                shutil.move(str(item_path), str(root / 'installer'))

        win = SibylMain()
        win.show()
        sys.exit(app.exec_())
    else:
        app.quit()
        sys.exit()

if __name__ == '__main__':
    main()
