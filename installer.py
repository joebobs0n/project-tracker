from copy import deepcopy
import time, sys, os, shutil, json
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pathlib import Path
from src.helpers import popup, getRoot
import src.literals as literals
import subprocess as sp


class InstallerApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__buildUi()
        self.install_edit.setText(str(Path('C:/Program Files/Sibyl')))
        self.default_edit.setText(str(Path(os.path.expanduser('~/Documents/Sibyl'))))
        self.__initTriggers()


    #! --- HELPER FUNCTIONS -----------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __initTriggers(self) -> None:
        self.install_button.clicked.connect(self.__installBrowse)
        self.default_button.clicked.connect(self.__defaultBrowse)
        self.buttonBox.accepted.connect(self.__install)
        self.buttonBox.rejected.connect(self.close)

    def __fileBrowser(self, which: str) -> Path:
        directory = QFileDialog.getExistingDirectory(
            self,
            f'{which} Directory',
            ''
        )
        directory = Path(directory)
        if directory.name != 'Sibyl':
            directory = directory / 'Sibyl'
        return directory


    #! --- TRIGGER FUNCTIONS ----------------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __installBrowse(self) -> None:
        install_path = self.__fileBrowser('Install')
        self.install_edit.setText(str(install_path))

    def __defaultBrowse(self) -> None:
        default_path = self.__fileBrowser('Default Saves')
        self.default_edit.setText(str(default_path))

    def __install(self) -> None:
        performInstall(self.install_edit.text(), self.default_edit.text())
        self.close()


    #! --- GENERATED BY QT DESIGNER (AND THEN MODIFIED BY ME) -------------------------------------
    #! --------------------------------------------------------------------------------------------

    def __buildUi(self) -> None:
        if not self.objectName():
            self.setObjectName('self')

        self.resize(445, 135)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QSize(445, 135))
        self.setMaximumSize(QSize(445, 135))

        if getattr(sys, 'frozen', False):
            icon_path = Path(sys.executable).parent / 'program_files/icons/settings.png'
            if not icon_path.exists():
                icon_path = Path(sys.executable).parent / 'icons/settings.png'
        else:
            icon_path = Path(__file__).parent / 'icons/settings.png'
        self.setWindowIcon(QIcon(str(icon_path)))

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName('centralwidget')
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName('verticalLayout')
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName('frame')
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.frame)
        self.formLayout.setObjectName('formLayout')
        self.formLayout.setHorizontalSpacing(5)
        self.formLayout.setVerticalSpacing(5)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.install_edit = QLineEdit(self.frame)
        self.install_edit.setObjectName('install_edit')
        self.install_edit.setMinimumSize(QSize(400, 0))
        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.install_edit)
        self.install_button = QPushButton(self.frame)
        self.install_button.setObjectName('install_button')
        self.install_button.setMaximumSize(QSize(22, 22))
        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.install_button)
        self.default_edit = QLineEdit(self.frame)
        self.default_edit.setObjectName('default_edit')
        self.default_edit.setMinimumSize(QSize(400, 0))
        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.default_edit)
        self.default_button = QPushButton(self.frame)
        self.default_button.setObjectName('default_button')
        self.default_button.setMaximumSize(QSize(22, 22))
        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.default_button)
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName('label_2')
        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)
        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName('label_3')
        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_3)
        self.verticalLayout.addWidget(self.frame)
        self.buttonBox = QDialogButtonBox(self.centralwidget)
        self.buttonBox.setObjectName('buttonBox')
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.buttonBox.button(QDialogButtonBox.Ok).setText('Install')
        self.verticalLayout.addWidget(self.buttonBox)
        self.setCentralWidget(self.centralwidget)

        self.__retranslateUi()
        QMetaObject.connectSlotsByName(self)

    def __retranslateUi(self) -> None:
        self.setWindowTitle(QCoreApplication.translate('self', 'Sibyl Installer', None))
        self.install_button.setText(QCoreApplication.translate('self', '...', None))
        self.default_button.setText(QCoreApplication.translate('self', '...', None))
        self.label_2.setText(QCoreApplication.translate('self', 'Install Location:', None))
        self.label_3.setText(QCoreApplication.translate('self', 'Default Saves Location:', None))


def criticalPopup(which: str, dir: Path) -> None:
    popup(
        getRoot(True),
        'Permission Error',
        (
            f'The installer was unable to write to {dir}.',
            f'Please choose a different {which} directory or rerun the installer as admin.'
        ),
        QMessageBox.Critical
    )

def performInstall(install_dir: str, default_dir: str) -> None:
    installer_root = getRoot(True)
    program_files_dir = installer_root / 'program_files'

    install_path = Path(install_dir)
    if not install_path.exists():
        try:
            os.mkdir(str(install_path))
        except PermissionError as e:
            criticalPopup('install', install_path)
            raise e
    default_path = Path(default_dir)
    if not default_path.exists():
        try:
            os.mkdir(str(default_path))
        except PermissionError as e:
            criticalPopup('default saves', default_dir)
            raise e
    backup_path = install_path / 'backup'
    if backup_path.exists():
        shutil.rmtree(str(backup_path))

    move_items = [l for l in install_path.iterdir() if l.name in literals.backup]
    if move_items != []:
        os.mkdir(str(backup_path))
    for item in move_items:
        shutil.move(str(item), str(backup_path / item.name))
    for item in program_files_dir.iterdir():
        if item.is_dir():
            shutil.copytree(str(item), str(install_path / item.name))
        elif item.is_file():
            shutil.copy(str(item), str(install_path / item.name))

    settings_path = install_path / literals.settings_filename
    settings = deepcopy(literals.settings_json)
    settings['default_dir'] = str(default_dir)
    settings['install_dir'] = str(install_dir)
    if settings_path.exists():
        shutil.copy(str(settings_path), str(backup_path / literals.settings_filename))
        with open(str(settings_path), 'r') as f:
            current_settings = json.load(f)
        settings = {**current_settings, **settings}
    with open(str(settings_path), 'w') as f:
        f.write(json.dumps(settings, indent=literals.tab_width))

def main() -> None:
    root = getRoot(True)
    app = QtWidgets.QApplication([])
    if not (root / literals.settings_filename).exists():
        win = InstallerApp()
        win.show()
        sys.exit(app.exec_())
    else:
        with open(str(root / literals.settings_filename), 'r') as f:
            settings = json.load(f)
        performInstall(settings['install_dir'], settings['default_dir'])
        app.quit()
        exe_path = Path(settings['install_dir']) / 'Sibyl.exe'
        sp.call(str(exe_path).split(' '), shell=True)
        sys.exit()

if __name__ == '__main__':
    time.sleep(0.5)
    main()
