#!/usr/bin/python3

from PyQt5 import uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog
import datetime as dt
from src.helpers import getTimeInfo


#* --- SETTINGS -----------------------------------------------------------------------------------
#* ------------------------------------------------------------------------------------------------

class SettingsDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('src/settings.ui', self)

    def exec_(self):
        super(SettingsDialog, self).exec_()
        return 'settings dialog closed'


#* --- ADD NOTE TO SELECTED PROJECT ---------------------------------------------------------------
#* ------------------------------------------------------------------------------------------------

class AddDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__submitContents = False
        uic.loadUi('src/add_note.ui', self)
        placeholdertext = [
            'Multiple notes can be added at a time by using separate lines',
            'Each line is converted to a bulletpoint (except tables and multi-line code blocks)',
            'All bulletpoints are timestamped unless the line begins with "!"',
            'Notes support simple Markdown (i.e. things such as links, emphasis, bold, underline etc)',
            'Empty line can be added with "</br>"'
        ]
        self.note_tedit.setPlaceholderText('\n'.join(placeholdertext))
        self.submit_button.clicked.connect(self.__submit)
        self.note_tedit.setFocus()

    def setup(self, current_pb, selected_proj):
        self.__current_pb = current_pb
        self.projselect_combo.addItems(list(self.__current_pb['projects'].keys()))
        self.projselect_combo.setCurrentText(selected_proj)

    def __submit(self):
        self.__submitContents = True
        self.close()

    def exec_(self):
        super(AddDialog, self).exec_()
        if self.__submitContents:
            return self.projselect_combo.currentText(), [l for l in self.note_tedit.toPlainText().split('\n')]
        else:
            return None, []


#* --- EDIT A GIVEN DAY'S NOTES FOR THE SELECTED PROJECT ------------------------------------------
#* ------------------------------------------------------------------------------------------------

class EditDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__submitContents = False
        uic.loadUi('src/edit_project.ui', self)
        placeholdertext = [
            'Edit markdown code for the selected project on a given day.',
            '',
            'Select which day\'s report to edit below.',
            'Edit the report in Markdown.'
        ]
        self.edit_tedit.setPlaceholderText('\n'.join(placeholdertext))
        self.edit_tedit.setFocus()
        self.edit_tedit.setEnabled(False)

        today = dt.date.today()
        self.date_date.setMaximumDate(today)
        self.date_date.setDate(today)

    def setup(self, current_pb, selected_proj):
        self.__current_pb = current_pb
        self.projselect_combo.addItems(list(self.__current_pb['projects'].keys()))
        self.projselect_combo.setCurrentText(selected_proj)
        self.name_edit.setText(selected_proj)
        self.priority_combo.setCurrentText(self.__current_pb['projects'][selected_proj]['priority'])

        self.submit_button.clicked.connect(self.__submit)
        self.projselect_combo.currentTextChanged.connect(self.__update)
        self.date_date.dateChanged.connect(self.__update)

        self.__update()

    def __update(self):
        self.name_edit.setText(self.projselect_combo.currentText())
        self.priority_combo.setCurrentText(self.__current_pb['projects'][self.projselect_combo.currentText()]['priority'])

        epoch, *_ = getTimeInfo(self.date_date.dateTime().toPyDateTime())
        epoch = str(epoch)
        proj_reports = self.__current_pb['projects'][self.projselect_combo.currentText()]['reports']
        if epoch in proj_reports.keys():
            self.edit_tedit.setEnabled(True)
            self.edit_tedit.setFocus()
            self.edit_tedit.setPlainText('\n\n'.join(proj_reports[epoch]))
        else:
            self.edit_tedit.setEnabled(False)
            self.name_edit.setFocus()
            self.edit_tedit.clear()

    def __submit(self):
        self.__submitContents = True
        self.close()

    def exec_(self):
        super(EditDialog, self).exec_()
        if self.__submitContents:
            name = self.name_edit.text()
            priority = self.priority_combo.currentText()
            proj = self.projselect_combo.currentText()
            date, *_ = getTimeInfo(self.date_date.dateTime().toPyDateTime())
            date = str(date)
            if self.edit_tedit.isEnabled():
                report = self.edit_tedit.toPlainText().split('\n\n')
            else:
                report = None
            return name, priority, proj, date, report
        else:
            return '', '', None, '', []


#* --- ADD NEW PROJECT WITH ACCOMPANYING TODO ITEMS -----------------------------------------------
#* ------------------------------------------------------------------------------------------------

class NewDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__submitContents = False
        self.__noUpdate = False
        uic.loadUi('src/new_project.ui', self)
        placeholdertext = [
            'Add new project and its corresponding initial todos.',
            'New todo items can be added later.',
            '',
            'Project templates can also be loaded by selecting a template from the combo box',
            'or saved by filling out this area with new project information and selecting the',
            '\'Add to Templates\' button.',
            '',
            'Example:',
            '<task name> - <priority [1-4]>',
            '- task 1',
            '- task 2',
            '- ...',
            '- task n'
        ]
        self.details_tedit.setPlaceholderText('\n'.join(placeholdertext))
        self.submit_button.clicked.connect(self.__submit)
        self.addtemplate_button.clicked.connect(self.__addTemplate)
        self.template_combo.currentIndexChanged.connect(self.__update)
        self.details_tedit.setFocus()

    def setup(self, current_pb):
        self.__current_pb = current_pb
        self.template_combo.addItems(list(self.__current_pb['templates'].keys()))
        self.__update()

    def __addTemplate(self):
        if self.details_tedit.toPlainText() != '':
            template = InputDialog()
            template.which('Template Name')
            tname = template.exec_()
            if tname != '':
                self.__current_pb['templates'][tname] = self.details_tedit.toPlainText()
            self.template_combo.addItem(tname)
            self.__noUpdate = True
            self.template_combo.setCurrentText(tname)

    def __update(self):
        if self.__noUpdate:
            self.__noUpdate = False
            return
        self.details_tedit.clear()
        cselection = self.template_combo.currentText()
        if cselection != '':
            self.details_tedit.setText(self.__current_pb['templates'][cselection])

    def __submit(self):
        self.__submitContents = True
        self.close()

    def exec_(self):
        super(NewDialog, self).exec_()
        if self.__submitContents:
            return self.details_tedit.toPlainText()
        else:
            return ''


#* --- GENERAL PURPOSE TEXT INPUT -----------------------------------------------------------------
#* ------------------------------------------------------------------------------------------------

class InputDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__submitContents = False
        uic.loadUi('src/input.ui', self)
        self.cancel_button.clicked.connect(self.__cancelled)
        self.submit_button.clicked.connect(self.__submit)

    def __submit(self):
        self.__submitContents = True
        self.close()

    def __cancelled(self):
        self.input_ledit.clear()
        self.close()

    def which(self, text):
        self.setWindowTitle(text)

    def exec_(self):
        super(InputDialog, self).exec_()
        if self.__submitContents:
            return self.input_ledit.text()
        else:
            return ''
