# TG Analytics — Admin Bot Extended Statistics

## Overview

Telegram bot that users add as admin to their channels (1-5 channels). When a user clicks "Расширенная статистика" on the channel page, the backend fetches detailed data on-demand via Bot API + Telethon, caches for 1 hour, and displays in the existing web UI.

**Users:** Internal team (15+ colleagues)
**Channels:** 1-5 own channels
**Trigger:** On-demand (button click on website), not scheduled

## Architecture

Two Telegram clients, one trigger:

```
User clicks "Расширенная статистика"
        │
        ▼
  GET /api/channels/{username}/extended
        │
        ├── Bot API (python-telegram-bot)
        │   ├── Verify bot is admin
        │   ├── Posts with replies, forwards, saves, reaction details
        │   └── Cache result 1 hour
        │
        └── Telethon (user account)
            ├── Admin log → join/leave events (30 days)
            ├── Participants → member list (up to 200)
            ├── Invite links → usage stats
            └── Cache result 1 hour
```

### Graceful Degradation

- Bot not admin → normal stats + banner "Add bot as admin"
- Telethon unavailable → Bot API data only, `telethon_available: false`
- Both unavailable → normal page (no extended section)

### Bot Setup

- Single bot via BotFather (e.g. `@tg_analytics_stats_bot`)
- `BOT_TOKEN` env var
- Polling mode (asyncio background task) — listens for `my_chat_member` updates
- When added as admin → sets `bot_is_admin = True` on channel record
- When removed → sets `bot_is_admin = False`
- Auto-analyzes channel if not yet in DB
- Minimal permissions: read messages, access admin log. No post/delete/ban.

## Data Sources

| Data | Bot API | Telethon |
|------|---------|----------|
| Posts + views + reactions + replies | ✓ | |
| Forwards count, saves | ✓ | |
| Reactions detail (per emoji) | ✓ | |
| Admin log (join/leave) | | ✓ |
| Member list | | ✓ |
| Invite link stats | | ✓ |

### Request Sequence (on button click)

```
1. Bot API: getChat()                    → verify admin     ~100ms
2. Bot API: getChatMemberCount()         → exact count      ~100ms
3. Bot API: channel messages             → posts+replies    ~500ms
4. Telethon: GetAdminLogRequest          → join/leave 30d   ~300ms
5. Telethon: GetParticipantsRequest      → up to 200 users  ~500ms
6. Telethon: GetExportedChatInvitesRequest → invite links   ~200ms
```

Total: ~2 seconds. Frontend shows spinner.

### Rate Limiting

- Cache 1 hour — repeated clicks return cached data
- Telethon: 1 second delay between steps 4-6
- If Telethon banned → return Bot API data only

## Database Schema

### New Tables

#### channel_members
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | |
| channel_id | INT FK | Channel reference |
| telegram_user_id | BIGINT | Telegram user ID |
| username | VARCHAR(100) NULL | @username if available |
| first_name | VARCHAR(255) NULL | First name |
| joined_at | TIMESTAMP NULL | Join date from admin log |
| left_at | TIMESTAMP NULL | Leave date (NULL = still subscribed) |

#### channel_admin_log
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | |
| channel_id | INT FK | Channel reference |
| event_type | VARCHAR(30) | "join", "leave", "edit_message", "delete_message", "pin" |
| user_id | BIGINT | Who performed the action |
| data | JSON NULL | Additional data |
| event_date | TIMESTAMP | When it happened |

#### channel_invite_links
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | |
| channel_id | INT FK | Channel reference |
| link | VARCHAR(255) | Invite link URL |
| creator_id | BIGINT NULL | Who created it |
| usage_count | INT DEFAULT 0 | Times used |
| fetched_at | TIMESTAMP | When fetched |

### Extended Fields on Existing Tables

#### posts — new columns
| Column | Type | Description |
|--------|------|-------------|
| replies_count | INT DEFAULT 0 | Number of replies/comments |
| saves_count | INT DEFAULT 0 | Number of saves |
| reactions_detail | JSON NULL | `{"👍": 15, "❤️": 8}` per-emoji breakdown |

#### channels — new columns
| Column | Type | Description |
|--------|------|-------------|
| bot_is_admin | BOOLEAN DEFAULT FALSE | Bot is admin in this channel |
| extended_fetched_at | TIMESTAMP NULL | Last extended stats fetch |

## API

### GET /api/channels/{username}/extended

On-demand extended statistics. Returns cached data if fresh (< 1 hour), otherwise fetches from Telegram.

**Response:**
```json
{
  "success": true,
  "data": {
    "bot_connected": true,
    "telethon_available": true,
    "fetched_at": "2026-03-31T12:00:00",
    "comments": {
      "total": 1234,
      "avg_per_post": 12.3,
      "top_posts": [
        {"post_id": 55, "text_preview": "...", "replies": 89}
      ]
    },
    "members": {
      "total": 812,
      "sample": [{"username": "user1", "first_name": "John", "joined_at": "..."}],
      "joins_7d": 45,
      "leaves_7d": 12,
      "net_growth_7d": 33
    },
    "traffic_sources": {
      "invite_links": [
        {"link": "...", "usage_count": 150, "creator": "admin1"}
      ],
      "top_forward_sources": ["@channel1", "@channel2"]
    },
    "post_details": {
      "avg_saves": 23,
      "avg_replies": 12,
      "reactions_breakdown": {"👍": 450, "❤️": 230, "🔥": 180}
    }
  }
}
```

**Error case (bot not admin):**
```json
{
  "success": true,
  "data": {
    "bot_connected": false,
    "bot_username": "tg_analytics_stats_bot",
    "instructions": "Add @tg_analytics_stats_bot as admin to your channel"
  }
}
```

## Frontend

No new pages. Changes to existing ChannelView:

### Button
Below metric cards, a button: **"Расширенная статистика"**
- Visible for all channels
- Click → calls `/extended` endpoint
- Shows spinner (~2s)
- Result: 4 collapsible blocks below the button

### Extended Blocks (when bot connected)

1. **Комментарии** — total, avg per post, top-3 most commented posts
2. **Подписчики** — joins/leaves за 7д, net growth, scrollable member list (up to 200)
3. **Источники трафика** — invite links table with usage counts
4. **Детализация постов** — avg saves, avg replies, emoji reaction breakdown (horizontal bar chart)

### Banner (when bot not connected)
Info banner with bot username and instruction: "Добавьте @bot_name в админы канала для расширенной статистики"

## Tech Stack Additions

- `python-telegram-bot` — Bot API client (add to requirements.txt)
- Alembic migration for new tables and columns
- No new frontend dependencies

## Environment Variables

```
# Bot (new)
BOT_TOKEN=<from BotFather>

# Telethon (existing)
TELEGRAM_API_ID=<existing>
TELEGRAM_API_HASH=<existing>
TELEGRAM_PHONE=<existing>
```

## Project Structure — New/Modified Files

```
backend/
  app/
    services/
      bot_client.py          # NEW: Bot API client (verify admin, fetch posts)
      extended_stats.py      # NEW: Orchestrator (Bot API + Telethon → combined response)
      telethon_client.py     # MODIFY: add admin_log, participants, invite_links methods
    api/
      channels.py            # MODIFY: add /extended endpoint
    models/
      member.py              # NEW: ChannelMember model
      admin_log.py           # NEW: ChannelAdminLog model
      invite_link.py         # NEW: ChannelInviteLink model
      channel.py             # MODIFY: add bot_is_admin, extended_fetched_at
      post.py                # MODIFY: add replies_count, saves_count, reactions_detail
    workers/
      bot_polling.py         # NEW: background task for my_chat_member updates
  alembic/
    versions/
      xxx_add_extended_stats.py  # NEW: migration
frontend/
  src/
    components/
      ExtendedStats.vue      # NEW: extended stats display (4 blocks)
      BotConnectBanner.vue   # NEW: "add bot" instruction banner
    views/
      ChannelView.vue        # MODIFY: add button + extended section
```
