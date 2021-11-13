
#? [VERSION]
version = 'v1.2.2'
version_notes = {
    'Feature': [
        ('Project Board Sorting', 'Projects, completed projects, and archived projects (upcoming feature) are now sorted within backend data structure. Sorting is by priority first and then alphabetically by name (case insensitive). This translates to the report window and projects veiwer showing the projects in this order.'),

    ],
    'Tweak': [
        ('Current Filepath now Path', 'Changed the internal variable storing the current filepath from string to Path object. Changed interracting code accordingly.'),
        ('Clear Backup on Close', 'Closing out a project board now deletes the backup file as well. This prevents the case when a project board is closed out, the program unexpectedly closes, and then upon boot, Sibyl loads a project board that the user has already closed (thus is likely unwanted).'),
        ('New Colors and Icons', 'Changed a few icons and replaced the teal color with orange for better visibility. The teal was blending in with the white app too well resulting in poor visibility.'),
        ('Elevated Privilege Executables', 'Executables now run with elevated privileges so installation and writing to directories with elevated read/write requirements are available.'),

    ],
    'Bug Fix': [
        ('Typos', 'Corrected typos in the README documentation.'),
        ('Moving Installer Assets Causing Crash', 'If the "installer" directory is not empty after an auto-update and installer assets needed to be moved from the root directory, a crash was happening due to the destination file already existing. This was resolved by providing absolute paths for the source and destination move paths.'),

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
tic_rate = 24
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
