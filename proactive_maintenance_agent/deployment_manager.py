import subprocess
import os


def run_command(command, cwd=None):

    result = subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)


def commit_and_push(repo_path, branch_name, commit_message):

    print("Initializing git repository...")

    if not os.path.exists(os.path.join(repo_path, ".git")):
        run_command("git init", cwd=repo_path)

    run_command(f"git checkout -B {branch_name}", cwd=repo_path)

    run_command("git add .", cwd=repo_path)

    run_command(f'git commit -m "{commit_message}"', cwd=repo_path)

    # add remote only if missing
    run_command(
        "git remote add origin https://github.com/" + os.getenv("GITHUB_REPO") + ".git",
        cwd=repo_path
    )

    run_command(f"git push -u origin {branch_name} --force", cwd=repo_path)