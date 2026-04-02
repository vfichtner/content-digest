from datetime import datetime, timezone, timedelta


class TelegramWrapper:
    def __init__(self, client):
        self.client = client

    async def get_posts(self, channel: str, days: int = 7) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        messages = await self.client.get_messages(channel, limit=100)

        posts = []
        for msg in messages:
            if msg.date < cutoff:
                continue
            if not msg.text:
                continue

            reactions_count = 0
            if msg.reactions and msg.reactions.results:
                reactions_count = sum(r.count for r in msg.reactions.results)

            replies_count = 0
            if msg.replies:
                replies_count = msg.replies.replies or 0

            posts.append({
                "id": msg.id,
                "text": msg.text,
                "date": msg.date.isoformat(),
                "views": msg.views or 0,
                "forwards": msg.forwards or 0,
                "reactions_count": reactions_count,
                "replies_count": replies_count,
                "engagement_score": (msg.views or 0) + (msg.forwards or 0) * 10 + reactions_count * 5 + replies_count * 3,
            })

        return sorted(posts, key=lambda p: p["engagement_score"], reverse=True)

    async def get_comments(self, channel: str, post_id: int) -> list[dict]:
        replies = await self.client.get_messages(channel, reply_to=post_id, limit=50)

        comments = []
        for reply in replies:
            if not reply.text:
                continue

            reactions_count = 0
            if reply.reactions and reply.reactions.results:
                reactions_count = sum(r.count for r in reply.reactions.results)

            comments.append({
                "id": reply.id,
                "text": reply.text,
                "date": reply.date.isoformat(),
                "reactions_count": reactions_count,
            })

        return comments
