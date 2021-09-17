#!/usr/bin/python3

from PyQt5 import uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog
import datetime as dt

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
            'Note(s) to add to the currently selected project.',
            'Multiple notes on separate lines.',
            'All notes are timestamped.',
            'Notes will be added to project report for the day of submission.'
        ]
        self.note_tedit.setPlaceholderText('\n'.join(placeholdertext))
        self.submit_button.clicked.connect(self.__submit)

    def __submit(self):
        self.__submitContents = True
        self.close()

    def exec_(self):
        super(AddDialog, self).exec_()
        if self.__submitContents:
            return self.note_tedit.toPlainText()
        else:
            return ''


#* --- EDIT A GIVEN DAY'S NOTES FOR THE SELECTED PROJECT ------------------------------------------
#* ------------------------------------------------------------------------------------------------

class EditDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__submitContents = False
        uic.loadUi('src/edit_note.ui', self)
        placeholdertext = [
            'snafu'
        ]
        self.edit_tedit.setPlaceholderText('\n'.join(placeholdertext))
        self.submit_button.clicked.connect(self.__submit)

        today = dt.date.today()
        qtoday = QDate(today.year, today.month, today.day)
        self.date_date.setMaximumDate(qtoday)
        self.date_date.setDate(qtoday)

    def __submit(self):
        self.__submitContents = True
        self.close()

    def exec_(self):
        super(EditDialog, self).exec_()
        if self.__submitContents:
            return self.edit_tedit.toPlainText()
        else:
            return ''


#* --- ADD NEW PROJECT WITH ACCOMPANYING TODO ITEMS -----------------------------------------------
#* ------------------------------------------------------------------------------------------------

class NewDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__submitContents = False
        uic.loadUi('src/new_project.ui', self)
        placeholdertext = [
            'fumtu'
        ]
        self.details_tedit.setPlaceholderText('\n'.join(placeholdertext))
        self.submit_button.clicked.connect(self.__submit)

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
        self.input_ledit.setPlaceholderText('bamf')
        self.cancel_button.clicked.connect(self.__cancelled)
        self.submit_button.clicked.connect(self.__submit)

    def __submit(self):
        self.__submitContents = True
        self.close()

    def __cancelled(self):
        self.input_ledit.clear()
        self.close()

    def exec_(self):
        super(InputDialog, self).exec_()
        if self.__submitContents:
            return self.input_ledit.text()
        else:
            return ''
