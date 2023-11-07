import os
import shutil
import tempfile

from github import Github, Auth
from git import Repo, Git
from loguru import logger

from line_counting import get_lines_in_repo

GH_TOKEN = os.getenv("GH_TOKEN")

# Params
language = "python"
license_type = "mit"
size_lower_bound = 1e3 # 1MB
size_upper_bound = 100e3 # 100MB
stars_lower_bound = 5000
contributors_lower_bound = 50
num_lines_lower_bound = 10e3
num_lines_upper_bound = 20e3

# Blacklisted users
blacklisted = ["openai"]

# Setup a temp dir to clone to
clone_dir = tempfile.TemporaryDirectory()

# Initialize a Github instance:
g = Github(GH_TOKEN)
query = f"language:{language} license:{license_type} size:{size_lower_bound}..{size_upper_bound} stars:>{stars_lower_bound}"
result = g.search_repositories(query)

filtered_repos = []
for repo in result:
    filtered_repos.append(repo)

# If you want to handle pagination manually, you can use the totalCount and totalPages properties
logger.info(f"Total repositories found: {result.totalCount}")

def clone_repo(repo_name):
    auth = Auth.Token(GH_TOKEN)
    github = Github(auth=auth)
    github_repo = github.get_repo(repo_name)
    clone_url = github_repo.clone_url.replace(
        "https://", f"https://{github.get_user().login}:{GH_TOKEN}@"
    )

    clone_path = os.path.join(clone_dir.name, repo_name)

    # We need to delete the directory if it already exists
    if os.path.isdir(clone_path):
        shutil.rmtree(clone_path)
    Git().clone(clone_url, clone_path)
    return clone_path

# Filter on number of contributors
enough_contributor_repos = []
for repo in filtered_repos:
    if repo.get_contributors().totalCount >= contributors_lower_bound:
        enough_contributor_repos.append(repo)

filtered_repos = enough_contributor_repos
logger.info(f"Remaining repos: {len(filtered_repos)}")

# Filter on activity
active_repos = []
for repo in filtered_repos:
    stats = repo.get_stats_commit_activity()
    breakpoint()

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
