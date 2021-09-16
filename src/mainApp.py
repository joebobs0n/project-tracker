
from PyQt5 import uic, QtGui
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox
import os, sys
from pathlib import Path

os.chdir(sys.path[0])

class PTApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('src/main.ui', self)
        self.setWindowIcon(QtGui.QIcon('icons/main.png'))
        self.__initTriggers()
        self.__unsaved_changes = False
        self.__current_filepath = None

    def closeEvent(self, evt):
        if self.__unsaved_changes:
            confirm = QMessageBox.warning(
                self,
                'Exit Without Saving?',
                'There are unsaved changes in the current project board.',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if confirm == QMessageBox.Save:
                self.__save()
            elif confirm == QMessageBox.Cancel:
                evt.ignore()

    def __initTriggers(self):
        self.load_menu.triggered.connect(self.__load)
        self.save_menu.triggered.connect(self.__save)
        self.saveas_menu.triggered.connect(self.__saveAs)
        self.close_menu.triggered.connect(self.__close)
        self.settings_menu.triggered.connect(self.__settings)
        self.exit_menu.triggered.connect(self.__exit)
        self.readme_menu.triggered.connect(self.__readme)
        self.github_menu.triggered.connect(self.__github)
        self.about_menu.triggered.connect(self.__about)

    def __load(self):
        self.__close()
        temp_filepath, _ = QFileDialog.getOpenFileName(
            self,
            'Open Project Board',
            '',
            'All Files (*);;json files (*.json)'
        )

        if Path(temp_filepath).exists() and Path(temp_filepath).suffix == '.json':
            self.__current_filepath = temp_filepath
            self.__openProjectBoard(self.__current_filepath)
        else:
            QMessageBox.warning(
                self,
                'Bad File',
                f'The provided filepath is either bad or DNE.\n{temp_filepath}'
            )

    def __save(self):
        if self.__current_filepath == None:
            self.__saveAs()
        else:
            self.__saveProjectBoard(self.__current_filepath)

    def __saveAs(self):
        temp_filepath, _ = QFileDialog.getSaveFileName(
            self,
            'Save Project Board',
            '',
            'All Files (*);;json files (*.json)',
            'json files (*.json)'
        )
        self.__saveProjectBoard(temp_filepath)

    def __close(self):
        status = ''
        if self.__unsaved_changes:
            confirm = QMessageBox.warning(
                self,
                'Close Out Project Board?',
                'There are unsaved changes in the current project board.\nAre you sure that you want to close it out?',
                QMessageBox.Yes | QMessageBox.Save | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            closeOut = False
            if confirm == QMessageBox.Yes:
                closeOut = True
                status = 'unsaved'
            elif confirm == QMessageBox.Save:
                self.__save()
                closeOut = True
                status = 'saved'
            else:
                status = 'cancelled'
        else:
            closeOut = True

        if closeOut:
            self.__clearAll()

        return status

    def __settings(self):
        pass

    def __exit(self):
        self.close()

    def __readme(self):
        QtGui.QDesktopServices.openUrl(QUrl('https://github.com/joebobs0n'))

    def __github(self):
        QtGui.QDesktopServices.openUrl(QUrl('https://github.com/joebobs0n'))

    def __about(self):
        info = [
            f'Version: 0.0.1',
            '',
            'Author: Andy Monk',
            'Email: czech.monk90@gmail.com'
        ]
        QMessageBox.about(self, 'Contact Info', '\n'.join(info))


    #! --- NON-TRIGGER FUNCTIONS ------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __openProjectBoard(self, openpath):
        print(f'open {openpath}')

    def __saveProjectBoard(self, savepath):
        print(f'save {savepath}')

    def __clearAll(self):
        print('clearing loaded data')
