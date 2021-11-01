
#? [VERSION]
version = 'v1.1.1'
version_notes = {
    'Feature': [

    ],
    'Tweak': [
        ('Version Notes Readability', 'Features, tweaks, and bug fixes compiled into single table for readability. Empty sections are no longer included.'),
        ('Auto Updater Clean Up', 'Auto updater now cleans up after itself.'),
        ('Auto Update Prompt Display New Version', 'When prompting the user if they want to install the newest version, said version is displayed.'),
        ('Main Script Name Change', 'Changed main script name from _main to Sibyl for clarity.'),
        ('Moved Github Token Home', 'Moved Github token from literals (committed file) to user\'s settings.json (non-committed file) and added appropriate existence checkers.'),
        ('Using Subprocess to Auto Launch', 'Using subprocess.Popen instead of os.system to call other executables to suppress visible console.'),

    ],
    'Bug Fix': [
        ('Auto Update Crashing', 'Fixed a bug where the auto updater was crashing while updating. Cause was bad python->shell commands.'),

    ]
}

#? [INSTALLER]
settings_filename = 'settings.json'
ignore_backup = [
    'Installer.exe',
    'program_files',
    'settings.json',
    'temp'
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
