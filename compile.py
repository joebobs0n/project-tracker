#!/usr/bin/python3

import argparse, os, shutil
import src.literals as literals
from pathlib import Path


def getArgs():
    args = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)
    args.add_argument('-d', '--debug', action='store_true', default=False,
                      help='flag to compile with console for debugging')
    args.add_argument('-z', '--zip', action='store_true', default=False,
                      help='flag to not zip the final files')
    return args.parse_args()

def main():
    args = getArgs()
    proj_root_path = Path('.')
    dist_path = proj_root_path / 'dist'
    dist_files_path = dist_path / 'program_files'
    ui_path = proj_root_path / 'ui'
    dist_ui_path = dist_files_path / 'ui'
    icons_path = proj_root_path / 'icons'
    dist_icons_path = dist_files_path / 'icons'
    main_path = proj_root_path / '_main.py'
    main_ico_path = icons_path / 'main.ico'
    main_bat_path = dist_files_path / 'sibyl-debugger.bat'
    installer_path = proj_root_path / 'installer.py'
    installer_ico_path = icons_path / 'installer.ico'
    installer_bat_path = dist_path / 'installer-debugger.bat'

    if dist_path.exists():
        shutil.rmtree(str(dist_path))
    debug = '' if args.debug else '--windowed '
    print(f'\033[92m-I-\033[0m Creating Sibyl.exe')
    os.system(f'pyinstaller.exe --onefile {debug}--name Sibyl --icon {main_ico_path} {main_path}')
    print(f'\033[92m-I-\033[0m Creating Installer.exe')
    os.system(f'pyinstaller.exe --onefile {debug}--name Installer --icon {installer_ico_path} {installer_path}')

    print('\033[92m-I-\033[0m Copying/moving assets')
    os.makedirs(str(dist_files_path))
    shutil.move(str(dist_path / 'Sibyl.exe'), str(dist_files_path / 'Sibyl.exe'))
    shutil.copytree(str(ui_path), str(dist_ui_path))
    shutil.copytree(str(icons_path), str(dist_icons_path), ignore=shutil.ignore_patterns('*.ico'))

    if args.debug:
        print(f'\033[92m-I-\033[0m Creating debugger batch files')
        with open(str(main_bat_path), 'w') as f:
            f.write('Sibyl.exe\npause')
        with open(str(installer_bat_path), 'w') as f:
            f.write('Installer.exe\npause')
    elif args.zip:
        print(f'\033[92m-I-\033[0m Zipping and cleaning up {dist_path}')
        shutil.make_archive(f'Sibyl-{literals.version}', 'zip', str(dist_path))
        shutil.rmtree(str(dist_path))
        os.mkdir(str(dist_path))
        shutil.move(f'Sibyl-{literals.version}.zip', str(dist_path))

        print(f'\n\033[92m-I-\033[0m Version Notes:')
        print_md = [f'# {literals.version}', '']
        for key, val in literals.version_notes.items():
            # print_md.extend([f'## {key}', '']')
            print_md.extend([f'|{key}|Notes|', '|:---|:---|'])
            for bullet, note in val:
                print_md.append(f'|{bullet}|{note}|')
            print_md.append('')
        print('\n'.join(print_md))

if __name__ == '__main__':
    main()
