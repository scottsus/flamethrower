sample_gitignore = """
# VSCode
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
*.code-workspace
# Local History for <a href="https://www.jcchouinard.com/python-with-vscode/">Visual Studio Code</a>
.history/
 
# Common credential files
**/credentials.json
**/client_secrets.json
**/client_secret.json
*creds*
*.dat
*password*
*.httr-oauth*
 
# Private Node Modules
node_modules/
creds.js
 
# Private Files
*.json
*.csv
*.csv.gz
*.tsv
*.tsv.gz
*.xlsx
 
 
# Mac/OSX
.DS_Store
 
 
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
 
# C extensions
*.so
 
# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
 
# PyInstaller
#  Usually these files are written by a <a href="https://www.jcchouinard.com/learn-python/">python</a> script from a template
#  before PyInstaller builds the exe, so as to inject date/other infos into it.
*.manifest
*.spec
 
# Installer logs
pip-log.txt
pip-delete-this-directory.txt
 
# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/
 
# Translations
*.mo
*.pot
 
# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
 
# Flask stuff:
instance/
.webassets-cache
 
# Scrapy stuff:
.scrapy
 
# Sphinx documentation
docs/_build/
 
# PyBuilder
.pybuilder/
target/
 
# <a href="https://www.jcchouinard.com/how-to-use-jupyter-notebook/">Jupyter Notebook</a>
.ipynb_checkpoints
 
# IPython
profile_default/
ipython_config.py
 
# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version
 
# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in <a href="https://www.jcchouinard.com/version-control/">version control.</a>
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock
 
# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/
 
# Celery stuff
celerybeat-schedule
celerybeat.pid
 
# SageMath parsed files
*.sage.py
 
# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
 
# <a href="https://www.jcchouinard.com/python-with-spyder-ide/">Spyder</a> project settings
.spyderproject
.spyproject
 
# Rope project settings
.ropeproject
 
# mkdocs documentation
/site
 
# mypy
.mypy_cache/
.dmypy.json
dmypy.json
 
# Pyre type checker
.pyre/
 
# pytype static type analyzer
.pytype/
 
# Cython debug symbols
cython_debug/
"""