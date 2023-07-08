from github import Github
import os

token = os.environ.get('GITHUB_TOKEN')

# First create a Github instance using an access token
g = Github(token)

def get_all_repos(query, limit=50):
    repo_list = list()
    result = g.search_repositories(query=query, sort='stars', order='desc')
    # Print repository name and the number of stars
    index = 1
    for repo in result:
        repo_list.append((repo.name, repo.clone_url, repo.default_branch, repo.stargazers_count))
        index +=1
        if index > limit:
            break
    return repo_list