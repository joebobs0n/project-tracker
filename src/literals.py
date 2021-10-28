
#? [VERSION]
version = 'v1.1.1'
version_notes = {
    'Features': [

    ],
    'Tweaks': [

    ],
    'Bug Fixes': [
        ('Cannot Check Version', 'App does not crash out when version checking is not avaliable. Two cases currently handled: request timeout (15 sec) and github rate limiting.')
    ]
}

#? [INSTALLER]
settings_filename = 'settings.json'
ignore_backup = [
    'Installer.exe',
    'program_files',
    'installer-debugger.bat',
    'sibyl-debugger.bat',
    'settings.json'
]
installer_cleanup = [
    'Installer.exe',
    'program_files'
]

#? [RUNTIME]
tic_rate = 50
tab_width = 4
undo_hist_on_save = 5

#? [GITHUB]
gh_repo = 'joebobs0n/project-tracker'
gh_token = None

#? [GUI STRINGS]
main_window_title = 'Sibyl - Project Tracker'
report_browser_placeholder = ' Nothing to report'
browser_filetypes = 'All Files (*);;Project Board (*.pjb);;JSON (*.json)'
browser_default_filetype = 'Project Board (*.pjb)'

#? [STRUCTURE]
priority_levels = [
    '',
    'high',
    'medium',
    'low',
    'none'
]
empty_project = {
    'priority':         None,
    'todos':            None,
    'completed_todos':  None,
    'notes':            None,
    'reports':          None
}
empty_pb = {
    'projects':         {},
    'completed':        {},
    'archived':         {},
    'templates':        {}
}
settings_json = {
    'default_dir':      None,
    'install_dir':      None
}
