import os
import shutil
import tempfile

from github import Github, Auth
from git import Repo, Git
from loguru import logger


# Params
language = "python"
license_type = "mit"
size_lower_bound = 1e3 # 1MB
size_upper_bound = 10e3 # 10MB
stars_lower_bound = 5000
contributors_lower_bound = 50
num_lines_lower_bound = 10e3
num_lines_upper_bound = 20e3


# Initialize a Github instance:
clone_dir = tempfile.TemporaryDirectory()
github = Github()
query = f"language:{language} license:{license_type} size:{size_lower_bound}..{size_upper_bound} stars:>{stars_lower_bound}"
result = github.search_repositories(query)

# If you want to handle pagination manually, you can use the totalCount and totalPages properties
logger.info(f"Total repositories found: {result.totalCount}")

def clone_repo(repo_name):
    github = Github()
    github_repo = github.get_repo(repo_name)
#    clone_url = github_repo.clone_url.replace(
#        "https://", f"https://{github.get_user().login}:{GH_TOKEN}@"
#    )

    clone_path = os.path.join(clone_dir.name, repo_name)

    # We need to delete the directory if it already exists
    if os.path.isdir(clone_path):
        shutil.rmtree(clone_path)
    Git().clone(github_repo.clone_url, clone_path)
    return clone_path

def get_lines_in_file(filename):
    try: 
        with open(filename, "r") as file:
            return sum(1 for line in file if line.strip())
    except FileNotFoundError:
        logger.error(f"Couldn't find {filename}!")
        return 0

def get_lines_in_repo(repo_path):
    # Walk through the repository directory tree
    python_files = []
    for subdir, dirs, files in os.walk(repo_path):
        # Exclude .git directory
        if '.git' in dirs:
            dirs.remove('.git')
        # Filter and count Python files
        python_files.extend([os.path.join(subdir, file) for file in files if file.endswith('.py')])

    num_lines = 0
    for filename in python_files:
        num_lines += get_lines_in_file(filename)
    logger.info(f"Number of files in the repository: {len(python_files)}")
    logger.info(f"Number of lines in the repository: {num_lines}")
    return num_lines





# Filter on number of contributors
filtered_repos = []
for page_number in range(result.totalCount // 30):  # 30 is the number of results per page
    page = result.get_page(page_number)
    for repo in page:
        if repo.get_contributors().totalCount >= contributors_lower_bound:
            filtered_repos.append(repo)

logger.info(f"Remaining repos: {len(filtered_repos)}")

# Filter on the number of lines
repos_with_right_lines = []
for repo in filtered_repos:
    logger.info(repo.full_name)
    logger.info(f"Num contributors: {repo.get_contributors().totalCount}")

    # clone the repo
    repo_path = clone_repo(repo.full_name)
    num_lines = get_lines_in_repo(repo_path)
    if num_lines > num_lines_lower_bound and num_lines < num_lines_upper_bound:
        repos_with_right_lines.append(repo)
filtered_repos = repos_with_right_lines



logger.info(f"Remaining repos: {len(filtered_repos)}")
for repo in filtered_repos:
    logger.info(repo.full_name)
