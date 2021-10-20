import sys, requests, shutil
import src.helpers as helpers
from src.literals import version
from PyQt5.QtWidgets import QMessageBox
from github import Github
from pathlib import Path


class Updater:
    #! --- CALLABLE UPDATER METHODS ---------------------------------------------------------------
    #! --------------------------------------------------------------------------------------------

    @classmethod
    def checkLatest(cls, github_repo: str, token: str, updateMinor=False) -> bool:
        if getattr(sys, 'frozen', False):
            root_dir = Path(sys.executable).parent
        else:
            root_dir = Path(__file__).parent.parent.parent
        gh = Github(login_or_token=token)
        repo = gh.get_repo(github_repo)
        latest = cls.__vconv(list(repo.get_tags())[0].name)
        current = cls.__vconv(version)
        if current[0] < latest[0]:
            helpers.popup(
                'Major Update Available',
                (
                    'Major updates are complete overhauls and cannot be auto-updated.',
                    f'Visit https://github.com/{github_repo} for more information.'
                ),
                QMessageBox.Critical
            )
        elif current[1] < latest[1]:
            helpers.popup(
                f'Minor Update Available.',
                'Would you like to install the minor update?',
                QMessageBox.Critical
            )
            updateMinor = False
            return cls.__autoUpdate(root_dir, repo)
        if updateMinor:
            cls.__autoUpdate(root_dir, repo)

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

        return False
