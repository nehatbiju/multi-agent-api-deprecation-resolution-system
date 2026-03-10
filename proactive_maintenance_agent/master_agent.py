import json
import time
from datetime import date
import os

# --- Mate 2 Tools ---
from email_fetcher import fetch_recent_emails
from email_parser import extract_deprecation
from research_agent import research_migration
from utils import calculate_urgency

# --- Mate 1 Tools ---
from integration_with_orchestrator import RAGIntegration
from codebase_loader import CodebaseLoader

# --- Your Orchestrator ---
from orchestrator import run_orchestrator


CHECK_INTERVAL_SECONDS = 60

KEYWORDS = [
    "deprecation",
    "retire",
    "migration",
    "sunset"
]


def subject_is_relevant(subject: str) -> bool:
    """Check if email subject contains deprecation keywords"""
    if not subject:
        return False
    return any(word in subject.lower() for word in KEYWORDS)


def setup_environment():
    """Ensure dummy codebase exists"""
    if not os.path.exists("./dummy_codebase"):
        print("📁 Generating dummy codebase...")
        CodebaseLoader.create_dummy_codebase()


def main():

    print("🚀 PROACTIVE MAINTENANCE AGENT STARTED\n")

    setup_environment()

    print("👀 Monitoring inbox for API deprecation alerts...")
    print("Press CTRL + C to stop\n")

    processed_email_uids = set()
    processed_deprecations = set()

    try:

        while True:

            print("=" * 60)
            print("📬 Checking inbox...")

            # --------------------------------------------------
            # PHASE 1 — EMAIL INGESTION
            # --------------------------------------------------

            emails = fetch_recent_emails()

            for email in emails:

                if email["uid"] in processed_email_uids:
                    continue

                processed_email_uids.add(email["uid"])

                if not subject_is_relevant(email["subject"]):
                    continue

                print(f"🔍 Relevant email detected: {email['subject']}")

                notice = extract_deprecation(email["body"])

                if not notice:
                    print("⚠️ No valid deprecation found in email")
                    continue

                dep_key = f"{notice.old_api_name}->{notice.new_api_name}"

                if dep_key in processed_deprecations:
                    print("⏩ Already processed this deprecation")
                    continue

                processed_deprecations.add(dep_key)

                print("\n🚨 NEW API DEPRECATION DETECTED")
                print(f"Old API: {notice.old_api_name}")
                print(f"New API: {notice.new_api_name}")

                urgency = calculate_urgency(notice.deadline)

                days_remaining = (notice.deadline - date.today()).days

                research = research_migration(notice)

                final_payload = {
                    "deprecation_info": notice.model_dump(),
                    "urgency": urgency,
                    "days_remaining": days_remaining,
                    "research_summary": research.model_dump() if research else None
                }

                with open("deprecation_payload.json", "w") as f:
                    json.dump(final_payload, f, indent=4, default=str)

                print("💾 Payload saved")

                # --------------------------------------------------
                # PHASE 2 — RAG CODE SEARCH
                # --------------------------------------------------

                print("\n⚙️ Starting RAG code search...")

                rag = RAGIntegration()

                rag.initialize()

                results = rag.find_deprecated_code(final_payload)

                rag.save_results(results)

                print("📂 Affected files saved")

                # --------------------------------------------------
                # PHASE 3 — AI CODE REWRITE
                # --------------------------------------------------

                print("\n🧠 Running AI code rewrite...")

                run_orchestrator()

                print("\n✅ PATCH PIPELINE COMPLETE\n")

            print(f"⏳ Waiting {CHECK_INTERVAL_SECONDS} seconds...\n")

            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:

        print("\n🛑 Monitoring stopped by user.")


if __name__ == "__main__":
    main()