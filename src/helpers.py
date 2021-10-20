import re, datetime, shutil, os, requests, time, sys
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from github import Github
from multiprocessing import Process
from src.magic_numbers import version
from pathlib import Path
from zipfile import ZipFile
from glob import glob
import subprocess as sp

def convertMarkdown(lines, timestamp):
    ret = []
    i = 0
    while i < len(lines):
        line = ''
        #? --- MD TABLES --------------------------------------------------------------------------
        if len(lines[i]) > 0 and lines[i][0] == '|':
            ret.append(f'- [{timestamp}] following table added')
            temp = []
            while i < len(lines) and lines[i][0] == '|':
                temp.append(lines[i])
                i += 1
            line = '\n'.join(temp)

        #? --- HTML -------------------------------------------------------------------------------
        elif lines[i] == '</br>':
            line = '` `'
            i += 1
        elif len(lines[i]) > 0 and lines[i][0] == '<':
            open_tag = re.findall(r'^<\w+\s|^<\w+>', lines[i])
            open_tag = lines[0] if len(open_tag) == 0 else open_tag[0]
            if open_tag[-1] != '>':
                open_tag = f'{open_tag.strip()}>'
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
            line = f'` `\n{line}'

        #? --- MD MULTI-LINE CODE -----------------------------------------------------------------
        elif re.findall('```.*', lines[i]):
            ret.append(f'- [{timestamp}] following code block added')
            temp = [lines[i]]
            i += 1
            while not re.findall('.*```', lines[i]):
                temp.append(lines[i])
                i += 1
            if re.findall('.+```', lines[i]) != []:
                temp.append(lines[i][:-3])
                temp.append('```')
            else:
                temp.append(lines[i])
            i += 1
            line = '\n'.join(temp)

        #? --- EMPTY LINE -------------------------------------------------------------------------
        elif lines[i] == '':
            line = lines[i]
            i += 1

        #? --- OTHER (BULLET POINTS) --------------------------------------------------------------
        else:
            line = lines[i]
            line = line.strip()
            # if line[0] == '*' or line[0] == '-':
            #     line = f'[{timestamp}] {line[1:].strip()}'
            # elif line[0] == '!':
            if line[0] == '!':
                line = line[1:].strip()
            else:
                line = f'[{timestamp}] {line}'
            line = f'- {line}'
            i += 1

        if line != '':
            ret.append(line)
    return ret

def getTimeInfo(conv_time):
    epoch = conv_time - datetime.timedelta(
        hours=conv_time.hour,
        minutes=conv_time.minute,
        seconds=conv_time.second,
        microseconds=conv_time.microsecond
    )
    epoch = epoch.timestamp()

    time = conv_time.strftime('%I:%M:%S %p').lower()
    if time[0] == '0':
        time = time[1:]

    date = f'{conv_time.month}/{conv_time.day}/{conv_time.year}'

    return int(epoch), time, date

def popup(title, message, level):
    if type(message) == tuple:
        text, infotext = message
    else:
        text = message
        infotext = None
    msg = QMessageBox()
    msg.setIcon(level)
    msg.setText(text)
    if infotext != None:
        msg.setInformativeText(infotext)
    msg.setWindowTitle(title)
    msg.setWindowIcon(QIcon('icons/dialog.png'))
    msg.exec_()

def checkLatest():
    gh = Github(login_or_token="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")
    repo = gh.get_repo('joebobs0n/project-tracker')
    latest = convVersion(list(repo.get_tags())[0].name)
    current = convVersion(version)

    if current[0] < latest[0]:
        popup(
            'Major Update Available',
            (
                'Major updates are complete overhauls and cannot be auto-updated.',
                'Please visit https://joebobs0n.github.io/project-tracker/ for more information.'
            ),
            QMessageBox.Critical
        )
    elif current[1] < latest[1]:
        popup(
            'Minor Update Available',
            'Would you like to install the minor update?',
            QMessageBox.Critical
        )
        return autoUpdate(repo)
    return True

def convVersion(ver):
    splt = ver.split('.')
    conv = [int(splt[0][1:]), float('.'.join(splt[1:]))]
    return conv

def updateFinalize(args):
    root_dir = args['root_dir']
    zip_file = args['zip_file']
    time.sleep(1)

    backup_dir = root_dir / f'{version}-backup'
    if backup_dir.exists():
        shutil.rmtree(str(backup_dir))
    os.makedirs(str(backup_dir))

    for item in ['src', 'icons', 'Sibyl.exe']:
        target = str(root_dir / item)
        dest = str(backup_dir / item)
        shutil.move(target, dest)
    with ZipFile(zip_file) as f:
        f.extractall()
    os.remove(zip_file)
    sp.Popen(str(root_dir / 'Sibyl.exe'), shell=True, stdout=sp.PIPE)
    # os.system(str(root_dir / 'Sibyl.exe'))

def autoUpdate(repo):
    if getattr(sys, 'frozen', False):
        root_dir = Path(sys.executable).parent
    else:
        root_dir = Path(__file__).parent.parent
    assets = repo.get_latest_release().get_assets()[0]
    assets_url = assets.browser_download_url
    zip_file = str(root_dir / assets.name)
    with open(zip_file, 'wb') as f:
        f.write(requests.get(assets_url).content)

    args = {
        'root_dir': root_dir,
        'zip_file': zip_file
    }
    p = Process(target=updateFinalize, args=[args])
    p.start()
    return False
