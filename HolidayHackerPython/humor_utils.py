import random
from typing import List

SUCCESS_MESSAGES = [
    "Congratulations! You legally hacked your calendar. 😎",
    "Productivity has left the chat. 😂",
    "Elite Holiday Hacker detected. 🏆",
    "Your boss will never know. 🤫",
    "Maximum chill achieved. 🧊",
    "This is the way. 🚀",
    "You've unlocked legendary work avoidance. 🎮",
    "HR wants to know your location. 📍"
]

FAILURE_MESSAGES = [
    "Unfortunately, your calendar has been secured. 😭",
    "The calendar gods are not in your favour. 🙅",
    "Your employer wins this round. 💼",
    "No hacks found — try a different range. 🔍",
    "Error 404: Holiday not found. 🤖",
    "Even we can't hack this calendar. 😔"
]

def get_efficiency_label(efficiency: float) -> str:
    if efficiency >= 5.0:
        return "🔥 LEGENDARY"
    if efficiency >= 4.0:
        return "🏆 ELITE"
    if efficiency >= 3.0:
        return "⭐ GREAT"
    if efficiency >= 2.0:
        return "👍 GOOD"
    if efficiency >= 1.5:
        return "🤔 OKAY"
    return "😐 MEH"

def get_random_success() -> str:
    return random.choice(SUCCESS_MESSAGES)

def get_random_failure() -> str:
    return random.choice(FAILURE_MESSAGES)

def build_bar(label: str, percent: int) -> str:
    filled = max(0, min(20, percent // 5))
    empty = 20 - filled
    return f"{label}: {'█' * filled}{'░' * empty} {percent}%"

def get_uselessness_meter(efficiency: float, leaves_used: int, total_leaves: int) -> List[str]:
    work_avoidance = min(100, int(efficiency * 20))
    leave_efficiency = min(100, int((leaves_used / total_leaves) * 100)) if total_leaves > 0 else 0
    productivity = max(0, 100 - work_avoidance)

    if work_avoidance >= 90:
        useless_level = "🔥 MAXIMUM"
    elif work_avoidance >= 70:
        useless_level = "⚡ HIGH"
    elif work_avoidance >= 50:
        useless_level = "📊 MODERATE"
    else:
        useless_level = "📉 LOW"

    return [
        build_bar("Work Avoidance", work_avoidance),
        build_bar("Leave Efficiency", leave_efficiency),
        build_bar("Productivity", productivity),
        f"Uselessness Level: {useless_level}"
    ]

def get_hacker_title(hacks_found: int) -> str:
    if hacks_found >= 10:
        return "🧙 Calendar Wizard"
    if hacks_found >= 5:
        return "🥷 Holiday Ninja"
    if hacks_found >= 3:
        return "🏄 Break Surfer"
    if hacks_found >= 1:
        return "🌱 Holiday Seedling"
    return "🆕 Newbie Hacker"
