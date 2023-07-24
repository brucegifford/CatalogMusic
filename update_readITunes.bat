call venv\Scripts\activate.bat
venv\Scripts\python.exe -m pip uninstall IReadiTunes
venv\Scripts\python.exe -m pip install git+https://github.com/brucegifford/IReadiTunes.git@master
venv\Scripts\python.exe -m pip freeze > requirements.txt