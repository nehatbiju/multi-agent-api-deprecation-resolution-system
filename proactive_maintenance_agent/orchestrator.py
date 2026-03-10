

import json
import os
import subprocess
import requests
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from github_agent import create_pull_request

# Load environment variables
load_dotenv()


def setup_gemini_brain():
    """Configures the Gemini model with a strict prompt"""

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    prompt = PromptTemplate.from_template(
        """
You are a Senior Python Developer.
Your job is to update deprecated API calls in the provided Python code.

OLD API TO REMOVE: {old_api}
NEW API TO USE: {new_api}

RULES:
1. Output ONLY valid, runnable Python code.
2. Do NOT include markdown formatting like ```python.
3. Do NOT include any explanations.
4. Keep all other logic exactly the same.

OLD DEPRECATED CODE:
{old_code}

MIGRATED CODE:
"""
    )

    return prompt | llm | StrOutputParser()


def run_orchestrator():

    print("🚀 Starting AI Orchestrator...\n")

    # ---------------------------------------------------
    # 1. Read Deprecation Payload
    # ---------------------------------------------------

    try:
        with open("deprecation_payload.json", "r") as f:
            payload = json.load(f)["deprecation_info"]

            old_api = payload["old_api_name"]
            new_api = payload["new_api_name"]

    except FileNotFoundError:
        print("❌ Error: deprecation_payload.json missing")
        return

    # ---------------------------------------------------
    # 2. Read RAG Results
    # ---------------------------------------------------

    try:
        with open("affected_files.json", "r") as f:
            rag_results = json.load(f)

    except FileNotFoundError:
        print("❌ Error: affected_files.json missing")
        return

    print(f"📥 Found {rag_results['files_found']} affected files.\n")

    # ---------------------------------------------------
    # 3. Initialize Gemini
    # ---------------------------------------------------

    brain = setup_gemini_brain()

    # ---------------------------------------------------
    # 4. Rewrite Code
    # ---------------------------------------------------

    for file_info in rag_results["affected_files"]:

        rel_filepath = file_info["filepath"]
        filepath = os.path.join("dummy_codebase", rel_filepath)

        old_code = file_info["file_content"]

        print(f"🧠 Rewriting file: {filepath}")
        
        import time
        while True:
            try:
                new_code = brain.invoke({
                "old_api": old_api,
                "new_api": new_api,
                "old_code": old_code
                })
                break
            except Exception as e:
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    print("⚠️ Gemini quota reached. Waiting 60 seconds before retry...")
                    time.sleep(60)
                else:
                    raise e

        clean_code = new_code.strip()

        if clean_code.startswith("```"):
            lines = clean_code.split("\n")

            if lines[0].startswith("```"):
                lines = lines[1:]

            if lines[-1].startswith("```"):
                lines = lines[:-1]

            clean_code = "\n".join(lines)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as f:
            f.write(clean_code)

        print(f"💾 Updated: {filepath}\n")

    print("✨ CODEBASE REWRITE COMPLETE\n")

    # ---------------------------------------------------
    # 5. Git Automation
    # ---------------------------------------------------

    branch_name = f"auto-update-{old_api.replace('.', '-')}-to-{new_api.replace('.', '-')}"
    branch_name = branch_name.replace("/", "-").replace(":", "-").replace(" ", "-")

    commit_msg = f"Auto patch: migrate {old_api} → {new_api}"

    repo_dir = "dummy_codebase"

    print("🔨 Running Git operations...\n")

    try:

        if not os.path.exists(os.path.join(repo_dir, ".git")):
            subprocess.run(["git", "init"], cwd=repo_dir, check=True)
            subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_dir, check=True)

        # create new branch or reset if it already exists
        subprocess.run(["git", "checkout", "-B", branch_name], cwd=repo_dir, check=True)

        subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)

        subprocess.run(
            [
                "git",
                "-c", "user.name=Proactive Agent",
                "-c", "user.email=agent@ai.local",
                "commit",
                "-m",
                commit_msg
            ],
            cwd=repo_dir,
            check=True
        )

        print(f"✅ Commit created on branch: {branch_name}")

        # push branch using the specific GitHub token
        github_token = os.getenv("GITHUB_TOKEN")
        github_repo = os.getenv("GITHUB_REPO")
        
        if github_token and github_repo:
            remote_url = f"https://{github_token}@github.com/{github_repo}.git"
            subprocess.run(
                ["git", "push", "-u", remote_url, branch_name],
                cwd=repo_dir,
                check=True
            )
        else:
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=repo_dir,
                check=True
            )

        print("🚀 Branch pushed to GitHub")

        # create PR
        pr_url = create_pull_request(branch_name)

    except Exception as e:
        print("⚠️ Git operation failed:", e)
        pr_url = None

    # ---------------------------------------------------
    # 6. Optional Slack Notification
    # ---------------------------------------------------

    slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

    if slack_webhook:
        
        pr_link = f"<{pr_url}|View Pull Request>" if pr_url else "*(PR could not be generated)*"

        msg = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🤖 Proactive API Maintenance Alert",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"A legacy API deprecation was detected and resolved automatically!\n\n*Deprecated API:* ` {old_api} `\n*Upgraded API:* ` {new_api} `\n*Branch:* ` {branch_name} `\n\n{pr_link}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": "The Proactive Maintenance Agent has submitted a patch to ensure no downstream breakage for the developer community. Please review and merge the PR."
                        }
                    ]
                }
            ]
        }

        try:
            requests.post(
                slack_webhook,
                json=msg,
                timeout=5
            )

            print("✅ Slack notification sent")

        except Exception as e:
            print("⚠️ Slack notification failed:", e)

    else:

        print("ℹ️ Slack webhook not configured (skipped)")

    print("\n✅ ORCHESTRATOR COMPLETE\n")


if __name__ == "__main__":
    run_orchestrator()