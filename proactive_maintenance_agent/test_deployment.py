from deployment_manager import commit_and_push
from github_agent import create_pull_request

repo_path = "dummy_codebase"

branch = "test-migration-branch"

commit_message = "Automated migration test"

commit_and_push(repo_path, branch, commit_message)

create_pull_request(branch)