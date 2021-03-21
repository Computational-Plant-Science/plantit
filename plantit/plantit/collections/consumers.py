import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class CollectionSessionConsumer(WebsocketConsumer):
    def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        print(f"Socket connected for user {self.username} collection session")
        async_to_sync(self.channel_layer.group_add)(f"sessions-{self.username}", self.channel_name)
        self.accept()

    def disconnect(self, code):
        print(f"Socket disconnected for user {self.username} collection session")
        async_to_sync(self.channel_layer.group_discard)(f"sessions-{self.username}", self.channel_name)

    def update_session(self, event):
        session = event['session']
        print(f"Received collection session update for user {self.username}: {session}")
        self.send(text_data=json.dumps({
            'session': session,
        }))
