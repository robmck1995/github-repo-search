import os
import shutil
import tempfile

from github import Github, Auth
from git import Repo, Git
from loguru import logger

from line_counting import get_lines_in_repo

GH_TOKEN = os.getenv("GH_TOKEN")

class RepoData:
    name: str
    contributors: int
    stars: int
    lines: int

# Params
language = "python"
license_type = "mit"
size_lower_bound = 1e3 # 1MB
size_upper_bound = 20e3 # 20MB
stars_lower_bound = 40000
active_weeks_cutoff = 4
contributors_lower_bound = 30
num_lines_lower_bound = 8e3
num_lines_upper_bound = 30e3

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

logger.info(f"Filtering on contributors (>{contributors_lower_bound})")
# Filter on number of contributors
enough_contributor_repos = []
for repo in filtered_repos:
    if repo.get_contributors().totalCount >= contributors_lower_bound:
        enough_contributor_repos.append(repo)

filtered_repos = enough_contributor_repos
logger.info(f"Remaining repos: {len(filtered_repos)}")

logger.info(f"Filtering on activity (active in last {active_weeks_cutoff})")
# Filter on activity
active_repos = []
for repo in filtered_repos:
    stats = repo.get_stats_commit_activity()
    total_commits_last_month = sum([s.total for s in stats[-1*active_weeks_cutoff:]])

    # Add if active in the last month
    if total_commits_last_month > 0:
        active_repos.append(repo)

filtered_repos = active_repos
logger.info(f"Remaining repos: {len(filtered_repos)}")

logger.info(f"Filtering on lines (from {num_lines_lower_bound} to {num_lines_upper_bound})")
# Filter on the number of lines
repos_with_right_lines = []
for repo in filtered_repos:
    logger.info(repo.full_name)

    # clone the repo
    repo_path = clone_repo(repo.full_name)
    num_lines = get_lines_in_repo(repo_path)
    if num_lines > num_lines_lower_bound and num_lines < num_lines_upper_bound:
        repos_with_right_lines.append(repo)
filtered_repos = repos_with_right_lines
logger.info(f"Remaining repos: {len(filtered_repos)}")



logger.info(f"Remaining repos: {len(filtered_repos)}")
for repo in filtered_repos:
    logger.info(f"Name: {repo.full_name}")
    logger.info(f"Contributors: {repo.get_contributors().totalCount}")
    logger.info(f"Stars: {repo.stargazers_count}")
