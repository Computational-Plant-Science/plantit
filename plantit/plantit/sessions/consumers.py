import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class SessionConsumer(WebsocketConsumer):
    def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.cluster = self.scope['url_route']['kwargs']['cluster']
        print(f"Socket connected for user {self.username} session on {self.cluster}")
        async_to_sync(self.channel_layer.group_add)(f"sessions-{self.username}-{self.cluster}", self.channel_name)
        self.accept()

    def disconnect(self, code):
        print(f"Socket disconnected for user {self.username} session on {self.cluster}")
        async_to_sync(self.channel_layer.group_discard)(f"sessions--{self.username}-{self.cluster}", self.channel_name)

    def session_update(self, event):
        session = event['session']
        print(f"Received session update for user {self.username} on {self.cluster}: {session}")
        self.send(text_data=json.dumps({
            'session': session,
        }))