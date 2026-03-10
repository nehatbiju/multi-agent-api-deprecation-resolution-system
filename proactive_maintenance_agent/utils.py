from datetime import date


def calculate_urgency(deadline):
    today = date.today()
    days_remaining = (deadline - today).days

    if days_remaining < 0:
        return "EXPIRED"
    elif days_remaining <= 7:
        return "CRITICAL"
    elif days_remaining <= 30:
        return "HIGH"
    elif days_remaining <= 60:
        return "MEDIUM"
    else:
        return "LOW"