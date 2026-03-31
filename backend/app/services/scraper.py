import re
from datetime import datetime
import httpx
from bs4 import BeautifulSoup

def _parse_view_count(text: str) -> int:
    text = text.strip().upper()
    if "K" in text:
        return int(float(text.replace("K", "")) * 1000)
    if "M" in text:
        return int(float(text.replace("M", "")) * 1_000_000)
    return int(re.sub(r"[^\d]", "", text) or "0")

def parse_tme_preview(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = None
    description = None
    avatar_url = None
    subscribers_count = 0

    og_title = soup.find("meta", property="og:title")
    if og_title:
        title = og_title.get("content")
    og_desc = soup.find("meta", property="og:description")
    if og_desc:
        description = og_desc.get("content")
    og_image = soup.find("meta", property="og:image")
    if og_image:
        avatar_url = og_image.get("content")
    extra = soup.find("div", class_="tgme_page_extra")
    if extra:
        text = extra.get_text()
        numbers = re.sub(r"[^\d]", "", text.split("subscriber")[0])
        if numbers:
            subscribers_count = int(numbers)
    return {
        "title": title,
        "description": description,
        "avatar_url": avatar_url,
        "subscribers_count": subscribers_count,
    }

def parse_tme_posts(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    posts = []
    for msg in soup.find_all("div", class_="tgme_widget_message"):
        data_post = msg.get("data-post", "")
        post_id = int(data_post.split("/")[-1]) if "/" in data_post else 0
        text_el = msg.find("div", class_="tgme_widget_message_text")
        text = text_el.get_text(strip=True) if text_el else None
        views_el = msg.find("span", class_="tgme_widget_message_views")
        views = _parse_view_count(views_el.get_text()) if views_el else 0
        time_el = msg.find("time")
        date = None
        if time_el and time_el.get("datetime"):
            date = time_el["datetime"]
        fwd_from = None
        fwd_el = msg.find("span", class_="tgme_widget_message_forwarded_from")
        if fwd_el:
            fwd_link = fwd_el.find("a")
            if fwd_link:
                fwd_text = fwd_link.get_text(strip=True)
                if fwd_text.startswith("@"):
                    fwd_from = fwd_text[1:]
        posts.append({
            "telegram_post_id": post_id,
            "text": text,
            "date": date,
            "views": views,
            "forwards": 0,
            "reactions": 0,
            "fwd_from_channel": fwd_from,
        })
    return posts

async def fetch_channel_preview(username: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://t.me/{username}",
            headers={"User-Agent": "Mozilla/5.0"},
            follow_redirects=True,
        )
        resp.raise_for_status()
        return parse_tme_preview(resp.text)

async def fetch_channel_posts(username: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://t.me/s/{username}",
            headers={"User-Agent": "Mozilla/5.0"},
            follow_redirects=True,
        )
        resp.raise_for_status()
        return parse_tme_posts(resp.text)
