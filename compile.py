#!/usr/bin/python3

import argparse, os, shutil, time, datetime
import src.literals as literals
from pathlib import Path
from glob import glob


def getArgs():
    args = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)
    args.add_argument('-d', '--debug', action='store_true', default=False,
                      help='compile with console and pausing batch files for debugging')
    args.add_argument('-z', '--zip', action='store_true', default=False,
                      help='zip the final files for github release')
    args.add_argument('-a', '--admin', action='store_true', default=False,
                      help='compile exes with admin privileges')
    return args.parse_args()

def info(msg, sep='\n'):
    print(f'\033[92m-I-\033[0m {msg}', end=sep, flush=False if sep == '\n' else True)

def main():
    dot_width = 35
    args = getArgs()
    proj_root_path = Path('.')
    build_path = proj_root_path / 'build'
    dist_path = proj_root_path / 'dist'
    dist_files_path = dist_path / 'program_files'
    ui_path = proj_root_path / 'ui'
    dist_ui_path = dist_files_path / 'ui'
    icons_path = proj_root_path / 'icons'
    dist_icons_path = dist_files_path / 'icons'
    main_path = proj_root_path / 'Sibyl.py'
    main_ico_path = icons_path / 'main.ico'
    main_bat_path = dist_files_path / 'sibyl-debugger.bat'
    installer_path = proj_root_path / 'installer.py'
    installer_ico_path = icons_path / 'settings.ico'
    installer_bat_path = dist_path / 'installer-debugger.bat'

    if dist_path.exists():
        shutil.rmtree(str(dist_path))
    debug = '' if args.debug else '--windowed '
    admin = '--uac-admin ' if args.admin else ''
    main_cmd = f'pyinstaller.exe {admin}--clean --log-level CRITICAL --onefile {debug}--name'

    info('Creating Sibyl.exe '.ljust(dot_width, '.'), sep=' ')
    tic = time.time()
    os.system(f'{main_cmd} Sibyl --icon {main_ico_path} {main_path}')
    toc = time.time()
    print(f'done [ \033[96m{datetime.timedelta(seconds=(toc-tic))}\033[0m ]')

    info('Creating Installer.exe '.ljust(dot_width, '.'), sep=' ')
    tic = time.time()
    os.system(f'{main_cmd} Installer --icon {installer_ico_path} {installer_path}')
    toc = time.time()
    print(f'done [ \033[96m{datetime.timedelta(seconds=(toc-tic))}\033[0m ]')

    info('Copying/moving assets '.ljust(dot_width, '.'), sep=' ')
    tic = time.time()
    os.makedirs(str(dist_files_path))
    shutil.move(str(dist_path / 'Sibyl.exe'), str(dist_files_path / 'Sibyl.exe'))
    shutil.copytree(str(ui_path), str(dist_ui_path))
    shutil.copytree(str(icons_path), str(dist_icons_path), ignore=shutil.ignore_patterns('*.ico'))
    toc = time.time()
    print(f'done [ \033[96m{datetime.timedelta(seconds=(toc-tic))}\033[0m ]')

    if args.debug:
        info('Creating debugger batch files '.ljust(dot_width, '.'), sep=' ')
        tic = time.time()
        with open(str(main_bat_path), 'w') as f:
            f.write('Sibyl.exe\npause')
        with open(str(installer_bat_path), 'w') as f:
            f.write('Installer.exe\npause')
        toc = time.time()
        print(f'done [ \033[96m{datetime.timedelta(seconds=(toc-tic))}\033[0m ]')
    elif args.zip:
        info(f'Zipping and cleaning up {dist_path} '.ljust(dot_width, '.'), sep=' ')
        tic = time.time()
        shutil.make_archive(f'Sibyl-{literals.version}', 'zip', str(dist_path))
        shutil.rmtree(str(dist_path))
        os.mkdir(str(dist_path))
        shutil.move(f'Sibyl-{literals.version}.zip', str(dist_path))
        toc = time.time()
        print(f'done [ \033[96m{datetime.timedelta(seconds=(toc-tic))}\033[0m ]')

    info('Cleaning up project root '.ljust(dot_width, '.'), sep=' ')
    tic = time.time()
    shutil.rmtree(str(build_path))
    for spec in glob(f'{proj_root_path}/*.spec'):
        os.remove(spec)
    toc = time.time()
    print(f'done [ \033[96m{datetime.timedelta(seconds=(toc-tic))}\033[0m ]')

    if args.zip:
        info('Version Notes:')
        print_md = [f'|Feature or Issue|Type|Notes|', '|:---|:---|:---|']
        for key, val in literals.version_notes.items():
            if len(val) > 0:
                for bullet, note in val:
                    print_md.append(f'|{bullet}|{key}|{note}|')
        print('\n'.join(print_md))

if __name__ == '__main__':
    main()
