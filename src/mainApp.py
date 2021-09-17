#!/usr/bin/python3

from PyQt5 import uic, QtGui
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox
import os, sys
from pathlib import Path
from src.dialogs import SettingsDialog, AddDialog, EditDialog, NewDialog, InputDialog
import datetime as dt


os.chdir(sys.path[0])

class PTApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('src/main.ui', self)

        self.__updateDates()
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

    def tic(self):
        date = dt.datetime.now()
        self.date = f'{date.month}/{date.day}/{date.year}'
        self.time = f'{date.hour}:{date.minute:02d}:{date.second:02d}'
        self.date_label.setText(f'{self.date} - {self.time}')

    def __statusMessage(self, msg):
        self.statusBar().showMessage(msg)

    def __initTriggers(self):
        #? --- TIME TRIGGER -----------------------------------------------------------------------
        timer = QTimer(self)
        timer.timeout.connect(self.tic)
        timer.start(100)

        #? --- MENU TRIGGERS ----------------------------------------------------------------------
        self.load_menu.triggered.connect(self.__load)
        self.save_menu.triggered.connect(self.__save)
        self.saveas_menu.triggered.connect(self.__saveAs)
        self.close_menu.triggered.connect(self.__close)
        self.settings_menu.triggered.connect(self.__settings)
        self.exit_menu.triggered.connect(self.__exit)
        self.readme_menu.triggered.connect(self.__readme)
        self.github_menu.triggered.connect(self.__github)
        self.about_menu.triggered.connect(self.__about)

        #? --- OTHER TRIGGERS ---------------------------------------------------------------------
        self.addreport_button.clicked.connect(self.__addReport)
        self.editreport_button.clicked.connect(self.__editReport)
        self.addproject_button.clicked.connect(self.__newProject)
        self.addtodo_button.clicked.connect(self.__addTodo)
        self.projects_tree.itemSelectionChanged.connect(self.__projectChanged)
        self.reportwhen_combo.currentTextChanged.connect(self.__updateDates)
        self.fromdate_date.dateChanged.connect(self.__updateReport)
        self.todate_date.dateChanged.connect(self.__updateReport)
        self.reportwhich_combo.currentTextChanged.connect(self.__updateReport)

    def __load(self):
        self.__close()
        temp_filepath, _ = QFileDialog.getOpenFileName(
            self,
            'Open Project Board',
            '',
            'All Files (*);;Project Board (*.pjb);;JSON (*.json)',
            'Project Board (*.pjb)'
        )

        tp = Path(temp_filepath)
        if tp.exists() and (tp.suffix == '.pjb' or tp.suffix == '.json'):
            self.__current_filepath = temp_filepath
            self.__openProjectBoard(self.__current_filepath)
        elif temp_filepath == '':
            pass
        else:
            QMessageBox.warning(
                self,
                'Bad File',
                '\n'.join([
                    'The provided filepath is either bad or DNE.',
                    f'{temp_filepath}'
                ])
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
            'All Files (*);;Project Board (*.pjb);;JSON (*.json)',
            'Project Board (*.pjb)'
        )
        self.__saveProjectBoard(temp_filepath)

    def __close(self):
        status = ''
        if self.__unsaved_changes:
            confirm = QMessageBox.warning(
                self,
                'Close Out Project Board?',
                '\n'.join([
                    'There are unsaved changes in the current project board.',
                    'Are you sure that you want to close it out?'
                ]),
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

    def __exit(self):
        self.close()

    def __readme(self):
        QtGui.QDesktopServices.openUrl(QUrl('https://joebobs0n.github.io/project-tracker/'))

    def __github(self):
        QtGui.QDesktopServices.openUrl(QUrl('https://github.com/joebobs0n/project-tracker'))

    def __about(self):
        info = [
            'Framework: PyQt5',
            'Icons: Candy Icons by EliverLara',
            f'Version: 0.0.1',
            '',
            'Author: Andy Monk',
            'Email: czech.monk90@gmail.com'
        ]
        QMessageBox.about(self, 'Contact Info', '\n'.join(info))

    def __newProject(self):
        new = NewDialog()
        retval = new.exec_()
        self.__statusMessage(retval)

    def __addReport(self):
        add = AddDialog()
        retval = add.exec_()
        self.__statusMessage(retval)

    def __addTodo(self):
        todo = InputDialog()
        retval = todo.exec_()
        self.__statusMessage(retval)

    def __editReport(self):
        edit = EditDialog()
        retval = edit.exec_()
        self.__statusMessage(retval)

    def __settings(self):
        # settings = SettingsDialog()
        # retval = settings.exec_()
        self.__statusMessage('settings needs to be implemented')

    def __projectChanged(self):
        self.__statusMessage('project selection changed')

    def __updateDates(self):
        today = dt.date.today()
        self.todate_date.setMaximumDate(today)
        self.fromdate_date.setMaximumDate(today)

        when = self.reportwhen_combo.currentText()
        if when == 'Today':
            self.__enableDates(False, False)
            qfrom = today
            qto = today
        elif when == 'Last Workday':
            self.__enableDates(False, False)
            qfrom = today - dt.timedelta(days=1 if today.weekday() != 0 else 3)
            qto = qfrom
        elif when == 'This Week':
            self.__enableDates(False, False)
            qfrom = today - dt.timedelta(days=today.weekday())
            qto = today
        elif when == 'Last Week':
            self.__enableDates(False, False)
            qfrom = today - dt.timedelta(days=today.weekday(), weeks=1)
            qto = qfrom + dt.timedelta(days=4)
        elif when == 'From':
            self.__enableDates(True, False)
            qto = today
        elif when == 'From-To':
            self.__enableDates(True, True)
        elif when == 'All':
            self.__enableDates(False, False)
            qto = today
            qfrom = dt.date(month=1, day=1, year=2021)
        else:
            pass

        if when != 'From' and when != 'From-To':
            self.fromdate_date.setDate(qfrom)
        if when != 'From-To':
            self.todate_date.setDate(qto)

    def __updateReport(self):
        self.__statusMessage('update report')


    #! --- NON-TRIGGER FUNCTIONS ------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __openProjectBoard(self, openpath):
        self.__statusMessage(f'Project board opened: {openpath}')

    def __saveProjectBoard(self, savepath):
        self.__statusMessage(f'Project board saved: {savepath}')

    def __clearAll(self):
        self.__statusMessage('Current project board cleared')

    def __enableDates(self, en_from, en_to):
        if en_from != self.fromdate_date.isEnabled():
            self.fromdate_date.setEnabled(en_from)
        if en_to != self.todate_date.isEnabled():
            self.todate_date.setEnabled(en_to)
