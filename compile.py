#!/usr/bin/python3

import argparse, os
from src.magic_numbers import version


def getArgs():
    args = argparse.ArgumentParser(formatter_class=argparse.MetavarTypeHelpFormatter)
    args.add_argument('-d', '--debug', action='store_true', default=False,
                      help='flag to compile with console for debugging')
    args.add_argument('-u', '--unzipped', action='store_true', default=False,
                      help='flag to not zip the final files')
    return args.parse_args()

def main():
    args = getArgs()
    system = os.name

    debug = '' if args.debug else '--windowed '
    print('\033[92m-I-\033[0m Compiling project')
    cmds = [
        'rm -rf ./dist',
        f'pyinstaller.exe --onefile {debug}--name Sibyl --icon ./icons/main.ico ./_main.py',
        'mkdir ./dist/icons ./dist/src',
        'cp ./icons/*.png ./dist/icons/.',
        'cp ./icons/main.ico ./dist/icons/.',
        'cp ./src/*.ui ./dist/src/.'
    ]
    for cmd in cmds:
        os.system(cmd)
    if args.debug:
        print('\033[92m-I-\033[0m Creating debug *.bat')
        os.system('echo ".\\Sibyl.exe\npause" > ./dist/sibyl-pause.bat')
    elif not args.unzipped:
        print('\033[92m-I-\033[0m Zipping and cleaning up ./dist')
        os.chdir('./dist')
        cmds = [
            f'zip -r ./sibyl-no-install-v{version}.zip ./icons ./src ./Sibyl.exe',
            'rm -rf ./icons ./src ./Sibyl.exe'
        ]
        for cmd in cmds:
            os.system(cmd)
        os.chdir('..')
    print('\033[92m-I-\033[0m Cleaning up ./')
    os.system('rm -rf ./build Sibyl.spec')

if __name__ == '__main__':
    main()
