import re

AD_KEYWORDS = [
    "реклама", "партнёрский", "партнерский", "спонсор", "промо",
    "#ad", "#реклама", "#промо",
]

AD_URL_PATTERNS = [
    r"utm_source=", r"utm_medium=", r"utm_campaign=",
    r"bit\.ly/", r"clck\.ru/", r"goo\.gl/",
]

AD_STRUCTURAL_PATTERNS = [
    r"подписывайтесь на @\w+",
    r"подписаться на @\w+",
]

def calculate_er(avg_views: int, subscribers: int) -> float:
    if subscribers == 0:
        return 0.0
    return round((avg_views / subscribers) * 100, 2)

def detect_ad_post(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    for keyword in AD_KEYWORDS:
        if keyword in text_lower:
            return True
    for pattern in AD_URL_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    for pattern in AD_STRUCTURAL_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False
