
#? [VERSION]
version = 'v1.1.0'
version_notes = {
    'Features': [
        ('Installer Added', 'Users can now use an installer to setup (move files and create settings file) their instance of Sibyl.'),
        ('Undo/Redo', 'Project board history is now tracked and the user can use the undo/redo buttons to traverse the history. Functions as expected.'),
        ('Check for Updates', 'Sibyl will check for updates upon startup. If minor updates are available, an auto-update will run if accepted by the user. If major updates are available, the user will be informed.'),
        ('Completed Todos Tracking', 'Completed todo items are now tracked; preparatory for future features.'),
        ('Version Notes', 'Running version notes kept in ./docs/version_history.md and is linked in README.md.'),

    ],
    'Tweaks': [
        ('Double Depth Bullets in Notes', 'In add notes, using "-" will create a second depth bullet point with no timestamp'),
        ('Save File Updater', 'If a save file generated from an older version of Sibyl is loaded, it will be updated to comply with the latest formatting.'),

    ],
    'Bug Fixes': [
        ('Save As Updates Filepath', 'Save As was not updating the file location for save. This has been resolved.'),
        ('Various Internal Inconsistencies', ''),

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
