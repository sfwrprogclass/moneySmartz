import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": ["pygame", "sys", "os", "random"],
    "include_files": ["assets/"],
    "excludes": []
}

# Base for the executable
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # This removes the console window

setup(
    name='MoneySmartz',
    version='1.0',
    description='Financial Life Simulator Game',
    options={"build_exe": build_exe_options},
    packages=['moneySmartz', 'moneySmartz.screens'],
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="MoneySmartz.exe",
            icon="assets/Money Smarts logo.png"
        )
    ],
    author='nicks',
    author_email='',
    url=''
)
