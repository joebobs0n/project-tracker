import re, datetime
import sys
from typing import Union
from pathlib import Path
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon

def convertMarkdown(lines: list[str], timestamp: str) -> list[str]:
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
            if line[0] == '!':
                line = f'- {line[1:].strip()}'
            elif line[0] == '-':
                line = f'  - {line[1:].strip()}'
            else:
                line = f'- [{timestamp}] {line}'
            i += 1

        if line != '':
            ret.append(line)
    return ret

def getTimeInfo(conv_time: datetime) -> tuple[int, str, str]:
    # if conv_time == None:
    #     conv_time = datetime.datetime.now()
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

def popup(root: Path, title: str, message: Union[tuple[str, str], str], level: QMessageBox) -> None:
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
    icon_path = None
    print(root)
    if (root / 'icons/dialog.png').exists():
        icon_path = root / 'icons/dialog.png'
    elif (root / 'program_files/icons/dialog.png').exists():
        icon_path = root / 'program_files/icons/dialog.png'
    msg.setWindowIcon(QIcon(str(icon_path)))
    return msg.exec_()

def getRoot(inRoot):
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent if inRoot else Path(__file__).parent.parent
