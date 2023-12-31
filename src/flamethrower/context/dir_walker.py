import os
import pathspec
import flamethrower.config.constants as config

def generate_directory_summary(start_path):
    gitignore = None
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as gitignore_file:
            gitignore = pathspec.PathSpec.from_lines('gitwildmatch', gitignore_file.readlines())

    with open(config.get_dir_structure_path(), 'w') as summary_file:
        process_directory(start_path, summary_file, gitignore=gitignore)

def process_directory(dir_path, summary_file, prefix='', gitignore=None):
    entries = os.listdir(dir_path)

    if gitignore:
        entries = [e for e in entries if not gitignore.match_file(os.path.join(dir_path, e))]
        entries = [e for e in entries if e != '.git']

    hidden_dirs = [d for d in entries if os.path.isdir(os.path.join(dir_path, d)) and d.startswith('.')]
    regular_dirs = [d for d in entries if os.path.isdir(os.path.join(dir_path, d)) and not d.startswith('.')]
    files = [f for f in entries if os.path.isfile(os.path.join(dir_path, f))]

    hidden_dirs.sort()
    regular_dirs.sort()
    files.sort()

    sorted_entries = hidden_dirs + regular_dirs + files
    for i, entry in enumerate(sorted_entries):
        path = os.path.join(dir_path, entry)
        if os.path.isdir(path):
            process_subdirectory(path, i, len(sorted_entries), summary_file, prefix, gitignore)
        else:
            write_file_entry(entry, i, len(sorted_entries), summary_file, prefix)

def process_subdirectory(path, index, total, summary_file, prefix, gitignore):
    readme_path = os.path.join(path, 'README.md')

    if os.path.exists(readme_path):
        summary = summarize_readme(readme_path)
        summary_line = f' // {summary}'
    else:
        summary_line = ''

    connector = '├──' if index < total - 1 else '└──'
    summary_file.write(f'{prefix}{connector} {os.path.basename(path)}{summary_line}\n')

    ext_prefix = '│   ' if index < total - 1 else '    '
    process_directory(path, summary_file, prefix=prefix + ext_prefix, gitignore=gitignore)

def write_file_entry(file_name, index, total, summary_file, prefix):
    connector = '├──' if index < total - 1 else '└──'
    summary_file.write(f'{prefix}{connector} {file_name}\n')

def summarize_readme(readme_path: str) -> str:
    with open(readme_path, 'r') as file:
        content = file.read()

    max_content_len = 100
    summary = content[:max_content_len].replace('\n', ' ')
    
    return summary