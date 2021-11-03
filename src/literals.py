
#? [VERSION]
version = 'v1.2.0'
version_notes = {
    'Feature': [
        ('Crash Reporting', 'Upon crashing, Sibyl creates a crash report and informs the user of its existence. The user at this point can leave an issues ticket on the Github or contact the dev team.'),
        ('Backup', 'Sibyl automatically creates a backup in the unfortunate case where it closes unexpectedly (crash, "end task" in task manager, "force close" upon restart/shut down, etc). If a backup is found upon booting Sibyl, the user will be prompted if they want to use it. Should they decline, the backup is overwritten.'),

    ],
    'Tweak': [
        ('New Icons', 'New icons have been added. More or less placeholder until more time can be invested into UI design.'),

    ],
    'Bug Fix': [
        ('Get Root Getting Wrong Path', 'The getRoot function was returning the wrong path because the function lives in the helpers file (in src) and would return its parent even when called from a script in the root directory.'),

    ]
}

#? [INSTALLER]
settings_filename = 'settings.json'
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
backup_filename = 'backup'
tic_rate = 50
tab_width = 4
hist_len_on_save = 5
gh_repo = 'joebobs0n/project-tracker'
gh_token = None
vars_serialize = {
    'path': [
        'root_path',
        'settings_path'
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
