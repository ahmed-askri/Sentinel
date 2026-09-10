import requests

class ConsoleNotifier:
    """Default — just prints. Same behavior as before."""
    def escalate(self, camera_id, summary, severity):
        print(f"\n🚨 ESCALATED — camera {camera_id} [{severity}]: {summary}\n")
        return "Escalation sent successfully."

    def flag_for_review(self, camera_id, reason):
        print(f"🙋 FLAGGED FOR HUMAN REVIEW — camera {camera_id}: {reason}")
        return "Flagged for human review."

class WebhookNotifier:
    """Real deployments: posts to Slack/Discord/your own server."""
    def __init__(self, url):
        self.url = url

    def escalate(self, camera_id, summary, severity):
        requests.post(self.url, json={"type": "escalation", "camera_id": camera_id, "summary": summary, "severity": severity})
        return "Escalation sent successfully."

    def flag_for_review(self, camera_id, reason):
        requests.post(self.url, json={"type": "human_review", "camera_id": camera_id, "reason": reason})
        return "Flagged for human review."

def build_notifier(method, webhook_url=""):
    if method == "webhook":
        return WebhookNotifier(webhook_url)
    return ConsoleNotifier()