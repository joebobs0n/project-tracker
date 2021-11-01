
#? [VERSION]
version = 'v1.1.4'
version_notes = {
    'Feature': [

    ],
    'Tweak': [

    ],
    'Bug Fix': [
        ('Completing Todo Cased Crash', 'Completing a todo item for a project started on an older version of Sibyl caused a crash. This was caused by the project board not having the "completed_todos" section for the project. Resolved by adding a project keys filler in the update save file method.'),

    ]
}

#? [INSTALLER]
settings_filename = 'settings.json'
backup = [
    'Sibyl.exe',
    'icons',
    'ui'
]
installer_cleanup = [
    'Installer.exe',
    'program_files',
    'zipfile'
]

#? [RUNTIME]
tic_rate = 50
tab_width = 4
hist_len_on_save = 5
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
