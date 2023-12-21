import os
import pathspec

def summarize_readme(readme_path):
    # Placeholder for text summarization logic
    # You would need a text summarization model or algorithm here
    with open(readme_path, 'r') as file:
        content = file.read()
    summary = content[:100]  # This is a simple truncation for demonstration
    return summary

def process_directory(dir_path, summary_file, prefix="", gitignore=None):
    files = []
    if not gitignore or not gitignore.match_file(dir_path):
        files = os.listdir(dir_path)
        files = [f for f in files if not gitignore or not gitignore.match_file(os.path.join(dir_path, f))]

    directories = [d for d in files if os.path.isdir(os.path.join(dir_path, d))]
    files = [f for f in files if os.path.isfile(os.path.join(dir_path, f))]

    entries = directories + files
    entries_count = len(entries)

    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        if os.path.isdir(path):
            readme_path = os.path.join(path, 'README.md')
            if os.path.exists(readme_path):
                summary = summarize_readme(readme_path)
                summary_line = f" # {summary}"
            else:
                summary_line = ""
            connector = "├──" if i < entries_count - 1 else "└──"
            summary_file.write(f"{prefix}{connector} {entry}{summary_line}\n")
            ext_prefix = "│   " if i < entries_count - 1 else "    "
            process_directory(path, summary_file, prefix=prefix + ext_prefix, gitignore=gitignore)
        else:
            connector = "├──" if i < entries_count - 1 else "└──"
            summary_file.write(f"{prefix}{connector} {entry}\n")

def generate_directory_summary(startpath):
    flamethrower_dir = os.path.join(startpath, '.flamethrower')
    if not os.path.exists(flamethrower_dir):
        os.makedirs(flamethrower_dir)
    
    gitignore = pathspec.PathSpec.from_lines('gitwildmatch', open('.gitignore').readlines()) if os.path.exists('.gitignore') else None

    with open(os.path.join(flamethrower_dir, 'summary.txt'), 'w') as summary_file:
        process_directory(startpath, summary_file, gitignore=gitignore)

# Call the function with the current working directory
generate_directory_summary(os.getcwd())
