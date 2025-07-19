# sse/consumers.py
import asyncio
import json
from channels.generic.http import AsyncHttpConsumer
from channels.db import database_sync_to_async
from polls.models import Poll, Vote
from django.db.models import Prefetch, Count

class SSEConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        poll_id = self.scope['url_route']['kwargs']['poll_id']
        await self.send_headers(headers=[
            (b'Content-Type', b'text/event-stream'),
            (b'Cache-Control', b'no-cache'),
            (b'Connection', b'keep-alive'),
        ])
        last_vote_id = 0
        
        while True:
            # Gunakan field poll langsung untuk query
            new_votes = await self.get_new_votes(poll_id, last_vote_id)
            if new_votes:
                last_vote_id = new_votes[-1].id
                data = await self.get_poll_data(poll_id)
                event = f"data: {json.dumps(data)}\n\n"
                await self.send_body(event.encode('utf-8'), more_body=True)
            await asyncio.sleep(1)

    @database_sync_to_async
    def get_new_votes(self, poll_id, last_vote_id):
        # Query menggunakan field poll langsung
        return list(Vote.objects.filter(
            poll_id=poll_id, 
            id__gt=last_vote_id
        ).order_by('id')[:100])  # Batasi untuk menghindari overload

    @database_sync_to_async
    def get_poll_data(self, poll_id):
        poll = Poll.objects.prefetch_related(
            Prefetch(
                'options',
                queryset=Option.objects.annotate(vote_count=Count('votes'))
        ).get(id=poll_id)
        
        return {
            'question': poll.question,
            'options': [
                {
                    'id': str(opt.id),
                    'text': opt.text,
                    'votes': opt.vote_count
                } for opt in poll.options.all()
            ]
        }