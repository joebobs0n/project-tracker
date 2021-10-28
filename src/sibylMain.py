from PyQt5 import QtGui, uic
from PyQt5.QtCore import QTimer, QUrl
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QTreeWidgetItem
from pathlib import Path
from copy import deepcopy
import json, datetime, re
import src.literals as literals
import src.helpers as helpers
import src.dialogs as dialogs


class SibylMain(QMainWindow):

    #! --- INITIALIZERS ---------------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__initVars()
        self.__loadSettings()
        self.__initGui()
        self.__clearAll()
        self.__updateDates()
        self.__initTriggers()
        # self.__updateReport()

    def __initVars(self) -> None:
        root = helpers.getRoot(False)
        self.__vars = {
            'version': literals.version,
            'root_path': root,
            'settings_path': root / literals.settings_filename,
            'tic_rate': literals.tic_rate,
            'current_filepath': None,
            'board_hist': [deepcopy(literals.empty_pb)],
            'current_board_index': 0,
            'last_save_board_index': 0,
            'date': None,
            'time': None,
            'today': None,
            'selected_proj': None,
            'selected_todo': None
        }

    def __initGui(self) -> None:
        uic.loadUi(self.__get('root_path') / 'ui/main.ui', self)
        self.report_browser.setPlaceholderText(literals.report_browser_placeholder)

        self.projects_tree.sortItems(0, 0)
        self.reportwhen_combo.setCurrentIndex(0)
        self.reportwhich_combo.setCurrentIndex(1)

    def __initTriggers(self) -> None:
        #? --- TIME TRIGGER -----------------------------------------------------------------------
        timer = QTimer(self)
        timer.timeout.connect(self.tic)
        timer.start(self.__get('tic_rate'))

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

        #? --- TOOLBAR TRIGGERS -------------------------------------------------------------------
        self.newnote_toolbar.triggered.connect(self.__addReport)
        self.editproject_toolbar.triggered.connect(self.__editReport)
        self.newproject_toolbar.triggered.connect(self.__newProject)
        self.settings_toolbar.triggered.connect(self.__settings)
        self.undo_toolbar.triggered.connect(self.__undo)
        self.redo_toolbar.triggered.connect(self.__redo)

        #? --- OTHER TRIGGERS ---------------------------------------------------------------------
        self.addproject_button.clicked.connect(self.__newProject)
        self.addtodo_button.clicked.connect(self.__addTodo)
        self.projects_tree.itemSelectionChanged.connect(self.__projectChanged)
        self.todo_list.itemSelectionChanged.connect(self.__todoChanged)
        self.reportwhen_combo.currentTextChanged.connect(self.__updateDates)
        self.fromdate_date.dateChanged.connect(self.__updateReport)
        self.todate_date.dateChanged.connect(self.__updateReport)
        self.reportwhich_combo.currentTextChanged.connect(self.__updateReport)
        self.removeproject_button.clicked.connect(self.__removeProject)
        self.completeproject_button.clicked.connect(self.__completeProject)
        self.removetodo_button.clicked.connect(self.__removeTodo)
        self.completetodo_button.clicked.connect(self.__completeTodo)


    #! --- REDEFENITION FROM SUPER ----------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def closeEvent(self, evt):
        if self.__get('unsaved'):
            confirm = QMessageBox.warning(
                self,
                'Exit Without Saving?',
                'The project board has unsaved changes.',
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if confirm == QMessageBox.Save:
                self.__save()
            elif confirm == QMessageBox.Cancel:
                evt.ignore()


    #! --- HEAVY LIFTERS --------------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __get(self, key: str, *data):
        #? Current Get Keys:
        #?   'unsaved': bool if current and saved hist indices are different
        #?   'projects': dict of projects (<name>: <proj_dict>)
        #?   'current_proj_board': entire project board snapshot from history (index current)
        #?   'todos': list of strings from currently selected proj; [] if no proj selected
        #?   'priority': priority of currently selected proj; -1 if no proj selected
        #?   'reports': all reports for a given project; [] if no proj selected
        #?   'selected_project': name of currently selected project
        #?   'selected_todo': name of currently selected todo
        #?   'hist_length': length of tracked board history
        #?   any key in self.__vars

        if key == 'unsaved':
            return self.__get('current_board_index') != self.__get('last_save_board_index')

        elif key == 'projects':
            return self.__get('board_hist')[self.__get('current_board_index')]['projects']

        elif key == 'current_proj_board':
            return self.__get('board_hist')[self.__get('current_board_index')]

        elif key == 'todos':
            try:
                proj = data[0]
            except IndexError:
                proj = self.__get('selected_project')
            return self.__get('projects')[proj]['todos'] if proj != None else []

        elif key == 'priority':
            try:
                proj = data[0]
            except IndexError:
                proj = self.__get('selected_project')
            return self.__get('projects')[proj]['priority'] if proj != None else -1

        elif key == 'reports':
            try:
                proj = data[0]
            except IndexError:
                proj = self.__get('selected_project')
            return self.__get('projects')[proj]['reports'] if proj != None else []

        elif key == 'selected_project':
            item = self.projects_tree.currentItem()
            return item.text(1) if item != None else None

        elif key == 'selected_todo':
            item = self.todo_list.currentItem()
            return item.text() if item != None else None

        elif key == 'hist_length':
            return len(self.__get('board_hist'))

        elif key == 'setup_report_day':
            proj, new_proj_board = data
            if new_proj_board['projects'][proj]['reports'] == None:
                new_proj_board['projects'][proj]['reports'] = {}
            epoch, *_ = helpers.getTimeInfo(self.__get('date'))
            epoch = str(epoch)
            if epoch not in new_proj_board['projects'][proj]['reports'].keys():
                new_proj_board['projects'][proj]['reports'][epoch] = [
                    f'### {self.__get("today")} ({self.__get("date").strftime("%A")})'
                ]
            return new_proj_board, epoch

        return self.__vars[key]

    def __set(self, action: str, *data) -> None:
        #? Current Set Actions
        #?   'append_board_hist': trims history if when not latest and appends given board snapshot
        #?   'trim_board_hist': trims history from given to given
        #?   'add_new_project': adds new proj to copy of latest pb and appends to hist
        #?   'add_new_todo': adds new todo to copy of latest pb and appends to hist
        #?   'remove_project': removes proj from copy of latest pb and appends to hist
        #?   'remove_todo': removes todo from copy of latest pb and appends to hist
        #?   'complete_project': moves proj to completed in copy of latest pb and appends to hist
        #?   'complete_todo': moves todo to completed in copy of latest pb and appends to hist
        #?   'set_date': set __vars['date'] variable
        #?   'open_project_board': opens a new project board (resets history)
        #?   'save_project_board': saves pb to file, updates save index, and shortens history
        #?   'update_todo_order': reorders todos in visual order in copy of latest pb and appends
        #?       to history
        #?   'current_index_increment': increment current_board_index
        #?   'current_index_decrement': decrement current_board_index
        #?   'modify_notes': mods notes for proj on day in copy of latest pb and appends to hist
        #?   'modify_priority': mods priority for proj in copy of latest pb and appends to hist
        #?   'modify_name': mods name for proj in copy of latest pb and appends to hist
        #?   'add_report': adds report list to proj in copy of latest pb and appends to hist

        if action == 'append_board_hist':
            if (self.__get('current_board_index') + 1) < self.__get('hist_length'):
                cutoff_index = self.__get('current_board_index') + 1
                self.__set('trim_board_hist', 0, cutoff_index)
            self.__vars['board_hist'].append(data[0])
            self.__set('current_index_increment')

        elif action == 'trim_board_hist':
            start, stop = data
            self.__set('board_hist', self.__get('board_hist')[start:stop])

        elif action == 'add_new_project':
            proj_name, proj_body = data
            new_proj_board = deepcopy(self.__get('current_proj_board'))
            new_proj_board['projects'][proj_name] = proj_body
            self.__set('append_board_hist', new_proj_board)

        elif action == 'add_new_todo':
            new_proj_board = deepcopy(self.__get('current_proj_board'))
            new_proj_board['projects'][self.__get('selected_project')]['todos'].append(data[0])
            self.__set('append_board_hist', new_proj_board)

        elif action == 'remove_project':
            new_proj_board = deepcopy(self.__get('current_proj_board'))
            del new_proj_board['projects'][data[0]]
            self.__set('append_board_hist', new_proj_board)

        elif action == 'remove_todo':
            new_proj_board = deepcopy(self.__get('current_proj_board'))
            idx = self.__get('todos').index(data[0])
            del new_proj_board['projects'][self.__get('selected_project')]['todos'][idx]
            self.__set('append_board_hist', new_proj_board)

        elif action == 'complete_project':
            new_proj_board = deepcopy(self.__get('current_proj_board'))
            new_proj_board['completed'][data[0]] = new_proj_board['projects'].pop(data[0])
            self.__set('append_board_hist', new_proj_board)

        elif action == 'complete_todo':
            new_proj_board = deepcopy(self.__get('current_proj_board'))
            selected_proj = self.__get('selected_project')
            new_pb_selected_proj = new_proj_board['projects'][selected_proj]
            idx = self.__get('todos').index(data[0])
            if new_pb_selected_proj['completed_todos'] == None:
                new_pb_selected_proj['completed_todos'] = []
            new_pb_selected_proj['reports']
            completed_todo = new_pb_selected_proj['todos'].pop(idx)
            new_proj_board, epoch = self.__get('setup_report_day', selected_proj, new_proj_board)
            new_pb_selected_proj['reports'][epoch].append(
                f'- [{self.__get("time")}] todo item __{completed_todo}__ completed'
            )
            new_pb_selected_proj['completed_todos'].append(completed_todo)
            self.__set('append_board_hist', new_proj_board)

        elif action == 'open_project_board':
            self.__set('board_hist', [data[0]])
            self.__set('current_board_index', 0)
            self.__set('last_save_board_index', 0)

        elif action == 'save_project_board':
            with open(data[0], 'w') as f:
                f.write(json.dumps(self.__get('current_proj_board'), indent=4))
            stop_idx = self.__get('current_board_index') + 1
            start_idx = stop_idx - literals.undo_hist_on_save
            if start_idx < 0:
                start_idx = 0
            new_index = self.__get('current_board_index') - start_idx
            self.__set('current_board_index', new_index)
            self.__set('last_save_board_index', new_index)
            self.__set('trim_board_hist', start_idx, stop_idx)

        elif action == 'update_todo_order':
            new_todos = []
            current_todos = self.__get('todos')
            for idx in range(len(current_todos)):
                new_todos.append(self.todo_list.item(idx).text())
            selected_proj_name = self.__get('selected_project')
            if (current_todos != new_todos) and (selected_proj_name != None):
                new_proj_board = deepcopy(self.__get('current_proj_board'))
                new_proj_board['projects'][selected_proj_name]['todos'] = new_todos
                self.__set('append_board_hist', new_proj_board)

        elif action == 'current_index_increment':
            current_index = self.__get('current_board_index')
            history_len = len(self.__get('board_hist'))
            if current_index < history_len - 1:
                self.__set('current_board_index', self.__get('current_board_index') + 1)

        elif action == 'current_index_decrement':
            current_index = self.__get('current_board_index')
            if current_index > 0:
                self.__set('current_board_index', self.__get('current_board_index') - 1)

        elif action == 'modify_notes':
            new_proj_board = deepcopy(self.__get('current_proj_board'))
            proj, day, report = data
            new_proj_board['projects'][proj]['reports'][day] = report
            self.__set('append_board_hist', new_proj_board)

        elif action == 'modify_priority':
            new_proj_board = deepcopy(self.__get('current_proj_board'))
            proj, priority = data
            new_proj_board['projects'][proj]['priority'] = priority
            self.__set('append_board_hist', new_proj_board)

        elif action == 'modify_name':
            new_proj_board = deepcopy(self.__get('current_proj_board'))
            name, proj = data
            new_proj_board['projects'][name] = new_proj_board['projects'].pop(proj)
            self.__set('append_board_hist', new_proj_board)

        elif action == 'add_report':
            proj, raw_report = data
            report_md = helpers.convertMarkdown(raw_report, self.__get('time'))
            if proj in self.__get('projects').keys() and len(report_md) > 0:
                new_proj_board = deepcopy(self.__get('current_proj_board'))
                new_proj_board, epoch = self.__get('setup_report_day', proj, new_proj_board)
                new_proj_board['projects'][proj]['reports'][epoch].extend(report_md)
                self.__set('append_board_hist', new_proj_board)

        else:
            self.__vars[action] = data[0]


    #! --- SETTINGS HANDLERS ----------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __loadSettings(self) -> None:
        settings_path = self.__get('root_path') / literals.settings_filename
        if settings_path.exists():
            with open(str(settings_path), 'r') as f:
                self.__userSettings = json.load(f)
        else:
            helpers.popup(
                self.__get('root'),
                'Settings File Not Found',
                (
                    'Settings file that contains crucial data is not found in the install directory.',
                    'Either rerun the installer or produce a settings file.'
                ),
                QMessageBox.Critical
            )
            raise FileNotFoundError('Missing settings.json')

    # def __saveSettings(self) -> bool:
    #     try:
    #         with open(str(self.__root / literals.settings_filename)) as f:
    #             f.write(json.dumps(self.__settings, indent=literals.tab_width))
    #     except Exception as e:
    #         print(f'\033[93m-W-\033[0m settings not saved upon call', e.__traceback__, sep='\n')
    #         return False
    #     return True


    #! --- TIC ------------------------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def tic(self) -> None:
        self.__set('date', datetime.datetime.now())
        _, time, today = helpers.getTimeInfo(self.__get('date'))
        self.__set('time', time)
        self.__set('today', today)
        self.date_label.setText(f'{self.__get("today")} - {self.__get("time")}')

        if self.__get('unsaved'):
            self.setWindowTitle(f'• {literals.main_window_title}')
        else:
            self.setWindowTitle(literals.main_window_title)

        if self.__get('current_filepath') != None:
            pb_name = Path(self.__get('current_filepath'))
            pb_name = pb_name.name.replace(pb_name.suffix, '')
        elif self.__get('current_filepath') == None and self.__get('unsaved'):
            pb_name = 'New Board'
        else:
            pb_name = 'None'
        self.pb_label.setText(f'Project Board: {pb_name}')

        current_index = self.__get('current_board_index')
        if current_index == self.__get('hist_length') - 1:
            self.redo_toolbar.setEnabled(False)
        else:
            self.redo_toolbar.setEnabled(True)
        if current_index == 0:
            self.undo_toolbar.setEnabled(False)
        else:
            self.undo_toolbar.setEnabled(True)

        self.__set('update_todo_order')

        # self.__statusMessage('history length:', len(self.__get('board_hist')))


    #! --- MENU TRIGGER FUNCTIONS -----------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __close(self) -> None:
        status = ''
        if self.__get('unsaved'):
            confirm = QMessageBox.warning(
                self,
                'Close Without Saving?',
                'The project board has unsaved changes.',
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

    def __load(self) -> None:
        status = self.__close()
        if status != 'cancel':
            load_filename, _ = QFileDialog.getOpenFileName(
                self,
                'Open Project Board',
                self.__userSettings['default_dir'],
                literals.browser_filetypes,
                literals.browser_default_filetype
            )
            load_filepath = Path(load_filename)
            if load_filepath.exists() and load_filepath.is_file():
                self.__set('current_filepath', load_filename)
                self.__openProjectBoard()
            elif load_filename != '':
                QMessageBox.warning(
                    self,
                    'Bad File',
                    '\n'.join([
                        'The provided filepath is either bad or DNE.',
                        f'Provided: ({load_filename})'
                    ])
                )

    def __save(self) -> None:
        if self.__get('current_filepath') == None:
            self.__saveAs()
        else:
            self.__saveProjectBoard(self.__get('current_filepath'))

    def __saveAs(self) -> None:
        save_filename, _ = QFileDialog.getSaveFileName(
            self,
            'Save Project Board',
            self.__userSettings['default_dir'],
            literals.browser_filetypes,
            literals.browser_default_filetype
        )
        self.__saveProjectBoard(save_filename)

    def __exit(self) -> None:
        self.close()

    def __readme(self) -> None:
        QtGui.QDesktopServices.openUrl(QUrl('https://joebobs0n.github.io/project-tracker/'))

    def __github(self) -> None:
        QtGui.QDesktopServices.openUrl(QUrl('https://github.com/joebobs0n/project-tracker/'))

    def __about(self) -> None:
        info = [
            'Framework: PyQt5',
            'Icons: Candy Icons by EliverLara',
            f'Version: {self.__get("version")}',
            '',
            'Author: Andy Monk',
            'Email: czech.monk90@gmail.com'
        ]
        QMessageBox.about(self, 'Contact Info', '\n'.join(info))


    #! --- TRIGGERED ------------------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __addReport(self) -> None:
        add = dialogs.AddDialog()
        add.setup(self.__get('current_proj_board'), self.__get('selected_project'))
        proj, raw_report = add.exec_()
        self.__set('add_report', proj, raw_report)
        self.__updateReport()

    def __addTodo(self) -> None:
        todo = dialogs.InputDialog()
        todo.which('New Todo Item')
        todo_text = todo.exec_()
        if todo_text != '':
            self.__set('add_new_todo', todo_text)
            self.__populateTodos()
            self.__statusMessage(f'todo item {todo_text.upper()} added')

    def __completeProject(self) -> None:
        name = self.__get('selected_project')
        self.__set('complete_project', name)
        self.__statusMessage(f'project {name.upper()} completed')
        self.__populateProjects()
        self.__populateTodos()
        self.__updateReport()

    def __completeTodo(self) -> None:
        todo = self.__get('selected_todo')
        self.__set('complete_todo', todo)
        self.__statusMessage(f'todo item {todo.upper()} completed')
        self.__populateTodos()
        self.__updateReport()

    def __settings(self) -> None:
        pass

    def __editReport(self) -> None:
        edit = dialogs.EditDialog()
        edit.setup(self.__get('current_proj_board'), self.__get('selected_project'))
        name, priority, proj, day, report = edit.exec_()
        if proj != None:
            if report != None:
                self.__set('modify_notes', proj, day, report)
            if priority != self.__get('priority'):
                self.__set('modify_priority', proj, priority)
                self.__populateProjects(self.__get('selected_project'))
            if name != proj:
                self.__set('modify_name', name, proj)
                self.__populateProjects(name)
            self.__statusMessage(f'{proj.upper()} report id {day} updated')
            self.__updateReport()

    def __newProject(self) -> None:
        new = dialogs.NewDialog()
        new.setup(self.__get('current_proj_board'))
        proj_details = new.exec_()

        project= [l.strip() for l in proj_details.split('\n') if l != '']
        header = []
        todos = []
        for line in project:
            if line[0] == '-':
                todos.append(line)
            else:
                header.append(line)
        if len(header) == 1:
            header = [h.strip() for h in header[0].split('-')]
            if len(header) == 1:
                priority = 4
            elif header[1] == '1' or header[1] == '2' or header[1] == '3' or header[1] == '4':
                priority = int(header[1])
            else:
                self.__statusMessage('Ill formed new project form: invalid priority level')
                return
            proj_name = header[0]
            body = deepcopy(literals.empty_project)
            body['priority'] = priority
            body['todos'] = [todo[1:].strip() for todo in todos]
            self.__set('add_new_project', proj_name, body)
            self.__populateProjects(proj_name)
            self.__statusMessage(f'Project {proj_name.upper()} added')
        else:
            self.__statusMessage('Ill formed new project form: too many headers detected')
            return

    def __projectChanged(self) -> None:
        if self.__get('selected_project') != None:
            self.__populateTodos()
            self.__setEnabled('projects', True)
            self.__setEnabled('todos', False)
        else:
            self.__setEnabled('projects', False)
            self.__setEnabled('todos', False)
        self.__updateReport()

    def __redo(self) -> None:
        self.__set('current_index_increment')
        self.__populateProjects()
        self.__populateTodos()
        self.__updateReport()
        self.__statusMessage('Redo')

    def __removeProject(self) -> None:
        name = self.__get('selected_project')
        self.__set('remove_project', name)
        self.__statusMessage(f'project {name.upper()} removed')
        self.__populateProjects()
        self.__populateTodos()
        self.__updateReport()

    def __removeTodo(self) -> None:
        todo = self.__get('selected_todo')
        self.__set('remove_todo', todo)
        self.__statusMessage(f'todo item {todo.upper()} removed')
        self.__populateTodos()
        self.__updateReport()

    def __todoChanged(self) -> None:
        if self.__get('selected_todo') != None:
            self.__setEnabled('todos', True)
        else:
            self.__setEnabled('todos', False)

    def __undo(self) -> None:
        self.__set('current_index_decrement')
        self.__populateProjects()
        self.__populateTodos()
        self.__updateReport()
        self.__statusMessage('Undo')

    def __updateDates(self):
        today = datetime.date.today()
        self.todate_date.setMaximumDate(today)
        self.fromdate_date.setMaximumDate(today)

        when = self.reportwhen_combo.currentText()
        if when == 'Today':
            self.__setEnabled('dates', False)
            qfrom = today
            qto = today
        elif when == 'Last Workday':
            self.__setEnabled('dates', False)
            qfrom = today - datetime.timedelta(days=1 if today.weekday() != 0 else 3)
            qto = qfrom
        elif when == 'This Week':
            self.__setEnabled('dates', False)
            qfrom = today - datetime.timedelta(days=today.weekday())
            qto = today
        elif when == 'Last Week':
            self.__setEnabled('dates', False)
            qfrom = today - datetime.timedelta(days=today.weekday(), weeks=1)
            qto = qfrom + datetime.timedelta(days=4)
        elif when == 'From':
            self.__setEnabled('date_from', True)
            self.__setEnabled('date_to', False)
            qto = today
        elif when == 'From-To':
            self.__setEnabled('dates', True)
        elif when == 'All':
            self.__setEnabled('dates', False)
            qto = today
            qfrom = datetime.date(month=1, day=1, year=2020)
        else:
            pass

        if when != 'From' and when != 'From-To':
            self.fromdate_date.setDate(qfrom)
        if when != 'From-To':
            self.todate_date.setDate(qto)

    def __updateReport(self) -> None:
        self.report_browser.clear()
        proj_sel = self.reportwhich_combo.currentText()
        report_projects = []
        if proj_sel == 'Selected':
            report_projects = [self.__get('selected_project')]
        elif proj_sel == 'All':
            report_projects = list(self.__get('projects').keys())
        else:
            if proj_sel == 'High Priority':
                proj_sel = 1
            elif proj_sel == 'Medium Priority':
                proj_sel = 2
            elif proj_sel == 'Low Priority':
                proj_sel = 3
            else:
                proj_sel = 4
            for name, obj in self.__get('projects').items():
                if obj['priority'] == proj_sel:
                    report_projects.append(name)

        fromtime, *_ = helpers.getTimeInfo(conv_time=self.fromdate_date.dateTime().toPyDateTime())
        totime, *_ = helpers.getTimeInfo(conv_time=self.todate_date.dateTime().toPyDateTime())
        try:
            if report_projects != None and len(report_projects) > 0:
                to_report = []
                for proj_name in report_projects:
                    proj_reports = self.__get('reports', proj_name)
                    if proj_reports != None and len(proj_reports) > 0:
                        this_proj = []
                        for epoch, report in self.__get('reports', proj_name).items():
                            epoch = int(epoch)
                            if epoch >= fromtime and epoch <= totime:
                                this_proj.extend(report)
                                this_proj.append('` `')
                        if len(this_proj) > 0:
                            this_proj.insert(0, f'# {proj_name}')
                            this_proj.insert(1, '----')
                            to_report.append('\n\n'.join(this_proj))
                # self.report_browser.setHtml('<p style="color:red">hi</p>')
                self.report_browser.setMarkdown('\n\n` `\n\n'.join(to_report))
            else:
                raise AttributeError
        except (AttributeError, KeyError):
            self.report_browser.clear()


    #! --- CALLED ---------------------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __openProjectBoard(self) -> None:
        filepath = self.__get('current_filepath')
        with open(str(filepath), 'r') as f:
            load_pb = json.load(f)
        if all(key in list(literals.empty_pb.keys()) for key in list(load_pb.keys())):
            load_pb = self.__updateSaveFile(load_pb)
            self.__set('open_project_board', load_pb)
            self.__populateProjects()
            self.__populateTodos()
            self.projects_tree.sortItems(0, 0)
            self.__statusMessage(f'Opened {filepath}')
        else:
            self.__statusMessage(f'Bad project board file: {filepath}')

    def __saveProjectBoard(self, savepath: str) -> bool:
        if savepath != '':
            self.__set('current_filepath', savepath)
            self.__set('save_project_board', savepath)
            self.__statusMessage(f'Saved as {savepath}')
        else:
            self.__statusMessage('Project board not saved')

    def __statusMessage(self, msg: str) -> None:
        self.statusBar().showMessage(msg)

    def __clearAll(self) -> None:
        self.__initVars()
        self.__populateProjects()
        self.__populateTodos()
        self.__setEnabled('projects', False)
        self.__setEnabled('todos', False)

    def __setEnabled(self, group: str, enabled: bool) -> None:
        groups = {
            'todos': [
                self.removetodo_button,
                self.completetodo_button
            ],
            'projects': [
                self.removeproject_button,
                self.completeproject_button,
                self.addtodo_button,
                self.newnote_toolbar,
                self.editproject_toolbar
            ],
            'dates': [
                self.fromdate_date,
                self.todate_date
            ],
            'date_from': [
                self.fromdate_date
            ],
            'date_to': [
                self.todate_date
            ]
        }

        for element in groups[group]:
            element.setEnabled(enabled)

    def __populateProjects(self, sel=None) -> None:
        self.projects_tree.setCurrentItem(None)
        self.projects_tree.clear()
        sel_qitem = None
        for name, obj in self.__get('projects').items():
            qitem = QTreeWidgetItem()
            if type(obj['priority']) == str:
                qitem.setText(0, obj['priority'])
            else:
                priority_text = f'{obj["priority"]}-{literals.priority_levels[obj["priority"]]}'
                qitem.setText(0, priority_text)
            qitem.setText(1, name)
            if name == sel:
                sel_qitem = qitem
            self.projects_tree.addTopLevelItem(qitem)
        if sel_qitem != None:
            self.projects_tree.setCurrentItem(sel_qitem)
        else:
            self.projects_tree.setCurrentItem(self.projects_tree.itemAt(0, 0))

    def __populateTodos(self) -> None:
        self.todo_list.setCurrentItem(None)
        self.todo_list.clear()
        todos = self.__get('todos')
        self.todo_list.addItems(todos)


    #! --- UPDATE SAVE FILE -----------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __updateSaveFile(self, save_pb: dict) -> dict:
        updated = deepcopy(save_pb)

        #? --- FILL OUT MISSING PROJECT BOARD SECTIONS --------------------------------------------
        for key, val in literals.empty_pb.items():
            if key not in updated.keys():
                updated[key] = val

        updated = self.__convertPriority(updated)
        updated = self.__sortByPriority(updated)

        return updated

    def __convertPriority(self, board: dict) -> dict:
        for section in ['projects', 'completed', 'archived']:
            for key, val in board[section].items():
                if type(val['priority']) == str:
                    priority_re = re.findall(r'^[0-9]+', val['priority'])
                    if len(priority_re) == 0:
                        raise ValueError(f'{section} [{key}] has priority [{val["priority"]}]: cannot resolve')
                    priority_int = int(priority_re[0])
                    board[section][key]['priority'] = priority_int
        return board

    def __sortByPriority(self, board: dict) -> dict:
        return board
