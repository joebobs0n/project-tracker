
#? [VERSION]
version = 'v1.2.2'
version_notes = {
    'Feature': [

    ],
    'Tweak': [
        ('Current Filepath now Path', 'Changed the internal variable storing the current filepath from string to Path object. Changed interracting code accordingly.'),

    ],
    'Bug Fix': [
        ('README Typos', 'Corrected typos in the README documentation.'),

    ]
}

#? [INSTALLER]
settings_filename = 'settings.json'
ver_backup_folder = 'previous_version'
ver_backup = [
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
backup_filename = 'backup.json'
tic_rate = 50
tab_width = 4
hist_len_on_save = 5
gh_repo = 'joebobs0n/project-tracker'
gh_token = None
vars_serialize = {
    'path': [
        'root_path',
        'settings_path',
        'current_filepath'
    ],
    'ignore': [
        'date'
    ]
}

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
    'none',
    'complete'
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
