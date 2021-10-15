#!/usr/bin/python3

from os import close
from PyQt5 import uic, QtGui
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QTreeWidgetItem
import json, re, os
from pathlib import Path
from src.dialogs import SettingsDialog, AddDialog, EditDialog, NewDialog, InputDialog
import datetime as dt
from copy import deepcopy


class PTApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('src/main.ui', self)
        self.report_browser.setPlaceholderText(' Nothing to report')
        self.__default_dir = Path(os.path.expanduser('~/Documents/Sibyl/'))
        if not Path(self.__default_dir).exists():
            os.makedirs(self.__default_dir / 'project_boards')
            os.makedirs(self.__default_dir / 'user_settings')

        self.__clearAll()
        self.__updateDates()
        self.__initTriggers()
        self.__updateReport()

        self.projects_tree.sortItems(0, 0)
        self.reportwhen_combo.setCurrentIndex(1)

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
        self.__date = dt.datetime.now()
        self.__today = f'{self.__date.month}/{self.__date.day}/{self.__date.year}'
        self.__time = self.__date.strftime('%I:%M%p').lower()
        if self.__time[0] == '0':
            self.__time = self.__time[1:]
        self.date_label.setText(f'{self.__today} - {self.__time}')
        self.__unsaved_changes = (self.__current_pb != self.__previous_save_state)

        if self.__unsaved_changes:
            self.setWindowTitle('• Sibyl - Project Tracker')
        else:
            self.setWindowTitle('Sibyl - Project Tracker')

        if self.__current_filepath != '':
            pb_name = Path(self.__current_filepath).name
            pb_name = str(pb_name).split('.')[0]
            self.pb_label.setText(f'Project Board: {pb_name}')
        elif self.__current_filepath == '' and self.__unsaved_changes == True:
            self.pb_label.setText('Project Board: New Board')
        else:
            self.pb_label.setText('Project Board: None')

        if self.__selectedProject == None or self.__selectedProject == '':
            try:
                self.projects_tree.setCurrentItem(self.projects_tree.itemAt(0,0))
            except AttributeError:
                pass

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
                str(self.__default_dir / 'project_boards'),
                'All Files (*);;Project Board (*.pjb);;JSON (*.json)',
                'Project Board (*.pjb)'
            )
            tp = Path(temp_filepath)
            if tp.exists() and (tp.suffix == '.pjb' or tp.suffix == '.json'):
                self.__current_filepath = temp_filepath
                self.__openProjectBoard()
            elif temp_filepath != '':
                QMessageBox.warning(
                    self,
                    'Bad File',
                    '\n'.join([
                        'The provided filepath is either bad or DNE.',
                        f'{temp_filepath}'
                    ])
                )

    def __save(self):
        if self.__current_filepath == '' or self.__current_filepath == None:
            self.__saveAs()
        else:
            self.__saveProjectBoard(self.__current_filepath)

    def __saveAs(self):
        self.__current_filepath, _ = QFileDialog.getSaveFileName(
            self,
            'Save Project Board',
            str(self.__default_dir / 'project_boards'),
            'All Files (*);;Project Board (*.pjb);;JSON (*.json)',
            'Project Board (*.pjb)'
        )
        self.__saveProjectBoard(self.__current_filepath)

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
            status = 'closed'
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
        if len(header) == 1:
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

    def __addReport(self):
        add = AddDialog()
        add.setup(self.__current_pb, self.__selectedProject)
        proj, retval = add.exec_()
        notes_md = self.__convertMarkdown(retval)
        if len(notes_md) != 0:
            epoch, _ = self.__getTimeInfo()
            epoch = str(epoch)
            if epoch not in self.__current_pb['projects'][proj]['reports'].keys():
                self.__current_pb['projects'][proj]['reports'][epoch] = [
                    f'### {self.__today} ({self.__date.strftime("%A")})'
                ]
            self.__current_pb['projects'][proj]['reports'][epoch].extend(notes_md)
        self.__updateReport()

    def __addTodo(self):
        todo = InputDialog()
        todo.which('New Todo Item')
        retval = todo.exec_()
        self.__selectedProjObj['todos'].append(retval)
        self.__statusMessage(f'todo item {retval.upper()} added')
        self.__populateTodos()

    def __editReport(self):
        edit = EditDialog()
        edit.setup(self.__current_pb)
        retval = edit.exec_()
        self.__statusMessage(retval)
        self.__updateReport()

    def __settings(self):
        settings = SettingsDialog()
        retval = settings.exec_()
        self.__statusMessage(retval)

    def __projectChanged(self):
        if self.projects_tree.currentItem() != None:
            self.__selectedProject = self.projects_tree.currentItem().text(1)
            self.__selectedProjObj = self.__current_pb['projects'][self.__selectedProject]
            self.__populateTodos()
            self.removeproject_button.setEnabled(True)
            self.completeproject_button.setEnabled(True)
            self.addtodo_button.setEnabled(True)
            self.newnote_toolbar.setEnabled(True)
            # self.editnote_toolbar.setEnabled(True)
        else:
            self.removeproject_button.setEnabled(False)
            self.completeproject_button.setEnabled(False)
            self.removetodo_button.setEnabled(False)
            self.completetodo_button.setEnabled(False)
            self.addtodo_button.setEnabled(False)
            self.newnote_toolbar.setEnabled(False)
            # self.editnote_toolbar.setEnabled(False)
        self.__updateReport()

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
        self.__selectedProjObj = None
        self.__statusMessage(f'project {self.__selectedProject.upper()} {action}')
        self.__selectedProject = None
        self.todo_list.clear()
        self.__populateProjects()
        self.__updateReport()

    def __completeProject(self):
        complete = self.__selectedProject
        self.__current_pb['completed'][complete] = deepcopy(self.__current_pb['projects'][complete])
        self.__removeProject('completed')

    def __removeTodo(self, action='removed'):
        remove = self.__selectedTodo
        index = self.__selectedProjObj['todos'].index(remove)
        del self.__selectedProjObj['todos'][index]
        self.__statusMessage(f'todo item {remove.upper()} {action}')
        self.__populateTodos()
        self.__updateReport()

    def __completeTodo(self):
        epoch, today_time = self.__getTimeInfo()
        epoch = str(epoch)
        proj_reports = self.__selectedProjObj['reports']
        if epoch not in proj_reports.keys():
            proj_reports[epoch] = [f'### {self.__today} ({self.__date.strftime("%A")})']
        todo_item = self.__selectedTodo
        proj_reports[epoch].append(f'- [{self.__time}] todo item __{todo_item}__ completed')
        self.__removeTodo('completed')

    def __updateReport(self):
        self.report_browser.clear()
        proj_sel = self.reportwhich_combo.currentText()
        report_projects = []
        if proj_sel == 'Selected':
            report_projects = [self.__selectedProject]
        elif proj_sel == 'All':
            report_projects = list(self.__current_pb['projects'].keys())
        else:
            if proj_sel == 'High Priority':
                proj_sel = '1-high'
            elif proj_sel == 'Medium Priority':
                proj_sel = '2-medium'
            elif proj_sel == 'Low Priority':
                proj_sel = '3-low'
            else:
                proj_sel = '4-none'
            for name, obj in self.__current_pb['projects'].items():
                if obj['priority'] == proj_sel:
                    report_projects.append(name)

        fromtime, _ = self.__getTimeInfo(conv_time=self.fromdate_date.dateTime().toPyDateTime())
        totime, _ = self.__getTimeInfo(conv_time=self.todate_date.dateTime().toPyDateTime())
        try:
            if report_projects != None and len(report_projects) > 0:
                to_report = []
                for proj_name in report_projects:
                    if len(self.__current_pb['projects'][proj_name]['reports']) > 0:
                        this_proj = []
                        for epoch, report in self.__current_pb['projects'][proj_name]['reports'].items():
                            epoch = int(epoch)
                            if epoch >= fromtime and epoch <= totime:
                                this_proj.extend(report)
                                # this_proj.append('```\n\n```')
                        if len(this_proj) > 0:
                            this_proj.insert(0, f'# {proj_name}')
                            this_proj.insert(1, '----')
                            to_report.append('\n\n'.join(this_proj))
                self.report_browser.setMarkdown('\n\n```\n\n```\n\n'.join(to_report))
            else:
                raise AttributeError
        except (AttributeError, KeyError):
            self.report_browser.clear()


    #! --- NON-TRIGGER FUNCTIONS ------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __openProjectBoard(self):
        self.__statusMessage(f'Opened {self.__current_filepath}')
        with open(self.__current_filepath, 'r') as f:
            check = json.load(f)
        if sorted(list(check.keys())) != sorted(['projects', 'completed', 'templates']):
            self.__statusMessage(f'Bad project board file: {self.__current_filepath}')
        else:
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
        todos = self.__selectedProjObj['todos']
        self.todo_list.addItems(todos)

    def __saveProjectBoard(self, savepath):
        if savepath != '':
            self.__statusMessage(f'Saved as {savepath}')
            with open(savepath, 'w') as f:
                f.write(json.dumps(self.__current_pb, indent=4))
            self.__previous_save_state = deepcopy(self.__current_pb)

    def __clearAll(self):
        self.__statusMessage('Current project board cleared')
        self.__current_filepath = ''
        self.__selectedProject = None
        self.__selectedProjObj = None
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

    def __getTimeInfo(self, conv_time=dt.datetime.today()):
        time = f'{conv_time.hour}:{conv_time.minute}'
        epoch = conv_time - dt.timedelta(
            hours=conv_time.hour,
            minutes=conv_time.minute,
            seconds=conv_time.second,
            microseconds=conv_time.microsecond
        )
        epoch = epoch.timestamp()
        return int(epoch), time

    def __convertMarkdown(self, lines):
        lines = [l for l in lines]
        ret = []
        i = 0
        while i < len(lines):
            line = ''
            if lines[i] != '':
                if lines[i][0] == '|':
                    ret.append(f'- [{self.__time}] following table added')
                    temp = []
                    while i < len(lines) and lines[i][0] == '|':
                        temp.append(lines[i])
                        i += 1
                    line = '\n'.join(temp)
                elif lines[i][0] == '<':
                    open_tag = re.findall(r'^<\w+\s|^<\w+>', lines[i])
                    open_tag = lines[0] if len(open_tag) == 0 else open_tag[0]
                    if open_tag[-1] != '>':
                        open_tag = f'{open_tag.strip()}>'
                    if open_tag[:2] != '</':
                        close_tag = list(open_tag)
                        close_tag.insert(1, '/')
                        close_tag = ''.join(close_tag)
                        if re.findall(close_tag, lines[i]) != []:
                            line = lines[i]
                            i += 1
                        else:
                            temp = []
                            while re.findall(close_tag, lines[i]) == []:
                                temp.append(lines[i])
                                i += 1
                            temp.append(lines[i])
                            i += 1
                            line = '\n'.join(temp)
                    else:
                        line = lines[i]
                        i += 1
                elif lines[i][:4] == '```':
                    ret.append(f'- [{self.__time}] following code block added')
                    temp = []
                    if re.findall('```.+', lines[i]) != []:
                        temp.append('```')
                        temp.append(lines[i][3:])
                    else:
                        temp.append(lines[i])
                    i += 1
                    while re.findall('```', lines[i]) == []:
                        temp.append(lines[i])
                        i += 1
                    if re.findall('.+```', lines[i]) != []:
                        temp.append(lines[i][:-3])
                        temp.append('```')
                    else:
                        temp.append(lines[i])
                    i += 1
                    line = '\n'.join(temp)
                else:
                    line = lines[i]
                    line = line.strip()
                    if line[0] == '*' or line[0] == '-':
                        line = line[1:].strip()
                    line = f'- [{self.__time}] {line}'
                    i += 1
                ret.append(line)
            else:
                i += 1
        return ret
