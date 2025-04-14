from setuptools import setup

APP = ['main.py']
DATA_FILES = ['financial_data.db']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter'],
    'plist': {
        'CFBundleName': 'Financial Helper',
        'CFBundleDisplayName': 'Financial Helper',
        'CFBundleGetInfoString': 'Track your finances',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025 Kingsley Shi'
    },
    'iconfile': 'icon.icns'  # Optional: Add an icon file if you have one
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)