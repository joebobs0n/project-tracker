import requests, shutil, os, stat
import src.helpers as helpers
import subprocess as sp
from PyQt5.QtGui import QIcon
from src.literals import version
from PyQt5.QtWidgets import QMessageBox
from github import Github
from pathlib import Path


class Updater:
    #! --- CALLABLE UPDATER METHODS ---------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    @classmethod
    def checkLatest(cls, github_repo: str, token: str) -> bool:
        root_dir = helpers.getRoot()
        gh = Github(login_or_token=token)
        repo = gh.get_repo(github_repo)
        ver = list(repo.get_tags())[0].name
        latest = cls.__vconv(ver)
        current = cls.__vconv(version)

        available = (current[0] < latest[0], current[1] < latest[1])
        if available[0]:
            helpers.popup(
                root_dir,
                'New Major Update Available',
                (
                    'Major updates are large overhauls and cannot be auto-updated.',
                    f'Visit https://github.com/{github_repo} for more information.'
                ),
                QMessageBox.Critical
            )
        elif available[1]:
            confirm = QMessageBox(
                QMessageBox.Warning,
                'New Minor Version Available',
                f'Would you like to install version {ver[1:]}?',
                QMessageBox.Ok | QMessageBox.Cancel,
                None
            )
            confirm.setWindowIcon(QIcon(str(root_dir / 'icons/dialog.png')))
            install = confirm.exec_()
            if install == QMessageBox.Ok:
                return cls.__autoUpdate(root_dir, repo)
        return True


    #! --- SUPPORT/HIDDEN FUNCTIONS ---------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    @classmethod
    def __vconv(cls, ver: str) -> list[int, float]:
        splt = ver.split('.')
        conv = [int(splt[0][1:]), float('.'.join(splt[1:]))]
        return conv

    @classmethod
    def __autoUpdate(cls, root_dir: Path, repo: str) -> bool:
        assets = repo.get_latest_release().get_assets()[0]
        assets_url = assets.browser_download_url
        zip_file = str(root_dir / assets.name)
        with open(zip_file, 'wb') as f:
            f.write(requests.get(assets_url).content)
        shutil.unpack_archive(str(zip_file), str(root_dir))
        if not (root_dir / 'zipfile').exists():
            os.mkdir(str(root_dir / 'zipfile'))
        shutil.move(zip_file, str(root_dir / 'zipfile' / assets.name))
        if (root_dir / 'installer').exists():
            shutil.rmtree(str(root_dir / 'installer'),
                          onerror=lambda func, path, _: (os.chmod(path, stat.S_IWRITE), func(path)))
        sp.call(str(root_dir / 'Installer.exe').split(' '), shell=True)
        return False
