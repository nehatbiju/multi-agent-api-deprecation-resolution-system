from imapclient import IMAPClient
import pyzmail
from config import EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD


def fetch_recent_emails(limit=10):
    """
    Fetch ONLY UNREAD emails from inbox.
    Returns list of dictionaries:
    {
        uid: int,
        subject: str,
        from: list,
        body: str
    }
    """

    emails = []

    try:
        with IMAPClient(EMAIL_HOST) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.select_folder("INBOX")

            # Fetch ONLY unread emails
            messages = server.search(["UNSEEN"])

            if not messages:
                return []

            # Take only latest N unread emails
            latest_uids = messages[-limit:]

            raw_messages = server.fetch(latest_uids, ["BODY[]", "FLAGS"])

            for uid in latest_uids:
                message = pyzmail.PyzMessage.factory(
                    raw_messages[uid][b"BODY[]"]
                )

                subject = message.get_subject()
                from_ = message.get_addresses("from")
                body = ""

                # Prefer plain text
                if message.text_part:
                    try:
                        body = message.text_part.get_payload().decode(
                            message.text_part.charset or "utf-8",
                            errors="ignore"
                        )
                    except Exception:
                        body = ""

                # Fallback to HTML
                elif message.html_part:
                    try:
                        body = message.html_part.get_payload().decode(
                            message.html_part.charset or "utf-8",
                            errors="ignore"
                        )
                    except Exception:
                        body = ""

                emails.append({
                    "uid": uid,
                    "subject": subject,
                    "from": from_,
                    "body": body
                })

        return emails

    except Exception as e:
        print("❌ Email fetch failed:", e)
        return []