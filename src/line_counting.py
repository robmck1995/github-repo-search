import os
import sys

from loguru import logger

def get_lines_in_file(filename):
    try: 
        with open(filename, "r") as file:
            return sum(1 for line in file if line.strip())
    except FileNotFoundError:
        logger.error(f"Couldn't find {filename}!")
        return 0

def get_lines_in_repo(repo_path, skip_tests):
    # Walk through the repository directory tree
    python_files = []
    for subdir, dirs, files in os.walk(repo_path):
        # Exclude .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        if skip_tests and 'tests' in dirs:
            dirs.remove('tests')
        # Filter and count Python files
        python_files.extend([os.path.join(subdir, file) for file in files if file.endswith('.py')])

    num_lines = 0
    for filename in python_files:
        num_lines += get_lines_in_file(filename)
    logger.info(f"Number of files in the repository: {len(python_files)}")
    logger.info(f"Number of lines in the repository: {num_lines}")
    return num_lines

if __name__ == "__main__":
    if len(sys.argv) > 2:
        get_lines_in_repo(sys.argv[1], True)
    else:
        get_lines_in_repo(sys.argv[1], False)

