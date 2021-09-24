#!/usr/bin/python3

from PyQt5 import uic, QtGui
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QTreeWidgetItem
import os, sys, json
from pathlib import Path
from src.dialogs import SettingsDialog, AddDialog, EditDialog, NewDialog, InputDialog
import datetime as dt
from copy import deepcopy


os.chdir(sys.path[0])

class PTApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('src/main.ui', self)

        self.__clearAll()
        self.__updateDates()
        self.__initTriggers()

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
        today = f'{date.month}/{date.day}/{date.year}'
        time = f'{date.hour}:{date.minute:02d}:{date.second:02d}'
        self.date_label.setText(f'{today} - {time}')
        self.__unsaved_changes = (self.__current_pb != self.__previous_save_state)
        if self.__unsaved_changes:
            self.setWindowTitle('• Project Tracker')
            self.save_menu.setEnabled(True)
            self.saveas_menu.setEnabled(True)
        else:
            self.setWindowTitle('Project Tracker')
            self.save_menu.setEnabled(False)
            self.saveas_menu.setEnabled(False)

    def __statusMessage(self, msg):
        self.statusBar().showMessage(msg)

    def __initTriggers(self):
        #? --- TIME TRIGGER -----------------------------------------------------------------------
        timer = QTimer(self)
        timer.timeout.connect(self.tic)
        timer.start(50)

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
        self.addproject_button.clicked.connect(self.__newProject)
        self.addtodo_button.clicked.connect(self.__addTodo)
        self.projects_tree.itemSelectionChanged.connect(self.__projectChanged)
        self.todo_list.itemSelectionChanged.connect(self.__todoChanged)
        self.reportwhen_combo.currentTextChanged.connect(self.__updateDates)
        self.fromdate_date.dateChanged.connect(self.__updateReport)
        self.todate_date.dateChanged.connect(self.__updateReport)
        self.reportwhich_combo.currentTextChanged.connect(self.__updateReport)
        self.newnote_toolbar.triggered.connect(self.__addReport)
        self.editnote_toolbar.triggered.connect(self.__editReport)
        self.newproject_toolbar.triggered.connect(self.__newProject)
        self.settings_toolbar.triggered.connect(self.__settings)
        self.removeproject_button.clicked.connect(self.__removeProject)
        self.completeproject_button.clicked.connect(self.__completeProject)
        self.removetodo_button.clicked.connect(self.__removeTodo)
        self.completetodo_button.clicked.connect(self.__completeTodo)

    def __load(self):
        status = self.__close()
        if status != 'cancel':
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
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            closeOut = False
            if confirm == QMessageBox.Discard:
                status = 'discard'
                closeOut = True
            elif confirm == QMessageBox.Save:
                status = 'save'
                self.__save()
                closeOut = True
            else:
                status = 'cancel'
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
        QtGui.QDesktopServices.openUrl(QUrl('https://github.com/joebobs0n/project-tracker/'))

    def __about(self):
        info = [
            'Framework: PyQt5',
            'Icons: Candy Icons by EliverLara',
            f'Version: 0.0.2',
            '',
            'Author: Andy Monk',
            'Email: czech.monk90@gmail.com'
        ]
        QMessageBox.about(self, 'Contact Info', '\n'.join(info))

    def __newProject(self):
        new = NewDialog()
        new.setup(self.__current_pb)
        retval = new.exec_()

        project = [l.strip() for l in retval.split('\n') if l != '']
        header = []
        todos = []
        for l in project:
            if l[0] == '-':
                todos.append(l)
            else:
                header.append(l)
        if len(header) != 1:
            return
        header = [h.strip() for h in header[0].split('-')]
        if len(header) == 1:
            priority = '4-none'
        elif header[1] == '1':
            priority = '1-high'
        elif header[1] == '2':
            priority = '2-medium'
        elif header[1] == '3':
            priority = '3-low'
        else:
            priority = '4-none'
        pname = header[0]
        todos = [t[1:].strip() for t in todos]

        self.__current_pb['projects'][pname] = {
            'priority': priority,
            'todos': todos,
            'reports': {}
        }
        self.__statusMessage(f'project {pname.upper()} added')

        qitem = QTreeWidgetItem()
        qitem.setText(0, priority)
        qitem.setText(1, pname)
        self.projects_tree.addTopLevelItem(qitem)

    #todo -----------------------------------------------------------------------------------------
    #todo -----------------------------------------------------------------------------------------
    def __addReport(self):
        if self.__selectedProject == None:
            self.__statusMessage('No project selected')
            return
        add = AddDialog()
        retval = add.exec_()
        self.__statusMessage(retval)

    def __addTodo(self):
        if self.__selectedProject == None:
            self.__statusMessage('No project selected')
            return
        todo = InputDialog()
        todo.which('New Todo Item')
        retval = todo.exec_()
        self.__current_pb['projects'][self.__selectedProject]['todos'].append(retval)
        self.__statusMessage(f'todo item {retval.upper()} added')
        self.__populateTodos()

    #todo -----------------------------------------------------------------------------------------
    #todo -----------------------------------------------------------------------------------------
    def __editReport(self):
        if self.__selectedProject == None:
            self.__statusMessage('No project selected')
            return
        edit = EditDialog()
        edit.setup(self.__current_pb)
        retval = edit.exec_()
        self.__statusMessage(retval)

    def __settings(self):
        settings = SettingsDialog()
        retval = settings.exec_()
        self.__statusMessage(retval)

    def __projectChanged(self):
        if self.projects_tree.currentItem() != None:
            self.__selectedProject = self.projects_tree.currentItem().text(1)
            self.__populateTodos()
            self.removeproject_button.setEnabled(True)
            self.completeproject_button.setEnabled(True)
            self.addtodo_button.setEnabled(True)
            self.newnote_toolbar.setEnabled(True)
            self.editnote_toolbar.setEnabled(True)
        else:
            self.removeproject_button.setEnabled(False)
            self.completeproject_button.setEnabled(False)
            self.removetodo_button.setEnabled(False)
            self.completetodo_button.setEnabled(False)
            self.addtodo_button.setEnabled(False)
            self.newnote_toolbar.setEnabled(False)
            self.editnote_toolbar.setEnabled(False)

    def __todoChanged(self):
        if self.todo_list.currentItem() != None:
            self.__selectedTodo = self.todo_list.currentItem().text()
            self.removetodo_button.setEnabled(True)
            self.completetodo_button.setEnabled(True)

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
            qfrom = dt.date(month=1, day=1, year=2020)
        else:
            pass

        if when != 'From' and when != 'From-To':
            self.fromdate_date.setDate(qfrom)
        if when != 'From-To':
            self.todate_date.setDate(qto)

    def __removeProject(self, action='removed'):
        del self.__current_pb['projects'][self.__selectedProject]
        self.__statusMessage(f'project {self.__selectedProject.upper()} {action}')
        self.todo_list.clear()
        self.__populateProjects()
        self.__selectedProject = None

    def __completeProject(self):
        complete = self.__selectedProject
        self.__current_pb['completed'][complete] = deepcopy(self.__current_pb['projects'][complete])
        self.__removeProject('completed')

    def __removeTodo(self, action='removed'):
        remove = self.__selectedTodo
        index = self.__current_pb['projects'][self.__selectedProject]['todos'].index(remove)
        del self.__current_pb['projects'][self.__selectedProject]['todos'][index]
        self.__statusMessage(f'todo item {remove.upper()} {action}')
        self.__populateTodos()

    def __completeTodo(self):
        date_seconds, today_time = self.__getTimeInfo()
        proj_reports = self.__current_pb['projects'][self.__selectedProject]['reports']
        if date_seconds not in proj_reports.keys():
            proj_reports[date_seconds] = ['# DATE HEADER HERE']
        todo_item = self.__selectedTodo
        proj_reports[date_seconds].append(f'- [ {today_time} ]: todo item {todo_item.upper()} completed')
        self.__removeTodo('completed')

    def __updateReport(self):
        self.__statusMessage('update report')


    #! --- NON-TRIGGER FUNCTIONS ------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __openProjectBoard(self, openpath):
        self.__statusMessage(f'Opened {openpath}')
        with open(openpath, 'r') as f:
            check = json.load(f)
        if sorted(list(check.keys())) != sorted(['projects', 'completed', 'templates']):
            self.__statusMessage(f'Bad project board file: {openpath}')
            return
        self.__current_pb = check
        self.__previous_save_state = deepcopy(self.__current_pb)
        self.__populateProjects()
        self.projects_tree.sortItems(0, 0)

    def __populateProjects(self):
        self.projects_tree.setCurrentItem(None)
        self.projects_tree.clear()
        for name, obj in self.__current_pb['projects'].items():
            qitem = QTreeWidgetItem()
            qitem.setText(0, obj['priority'])
            qitem.setText(1, name)
            self.projects_tree.addTopLevelItem(qitem)

    def __populateTodos(self):
        self.todo_list.setCurrentItem(None)
        self.todo_list.clear()
        todos = self.__current_pb['projects'][self.__selectedProject]['todos']
        self.todo_list.addItems(todos)

    def __saveProjectBoard(self, savepath):
        if savepath != '':
            self.__statusMessage(f'Saved as {savepath}')
            with open(savepath, 'w') as f:
                f.write(json.dumps(self.__current_pb, indent=4))
            self.__previous_save_state = deepcopy(self.__current_pb)

    def __clearAll(self):
        self.__statusMessage('Current project board cleared')
        self.__current_filepath = None
        self.__selectedProject = None
        self.__current_pb = {
            "projects": {},
            "completed": {},
            "templates": {}
        }
        self.__previous_save_state = deepcopy(self.__current_pb)
        self.projects_tree.setCurrentItem(None)
        self.projects_tree.clear()
        self.todo_list.clear()
        self.report_browser.clear()
        self.removeproject_button.setEnabled(False)
        self.completeproject_button.setEnabled(False)
        self.removetodo_button.setEnabled(False)
        self.completetodo_button.setEnabled(False)
        self.addtodo_button.setEnabled(False)
        self.newnote_toolbar.setEnabled(False)
        self.editnote_toolbar.setEnabled(False)

    def __enableDates(self, en_from, en_to):
        if en_from != self.fromdate_date.isEnabled():
            self.fromdate_date.setEnabled(en_from)
        if en_to != self.todate_date.isEnabled():
            self.todate_date.setEnabled(en_to)

    def __getTimeInfo(self):
        today = dt.datetime.today()
        time = f'{today.hour}:{today.minute}'
        epoch = today - dt.timedelta(
            hours=today.hour,
            minutes=today.minute,
            seconds=today.second,
            microseconds=today.microsecond
        )
        epoch = epoch.timestamp()
        return int(epoch), time
