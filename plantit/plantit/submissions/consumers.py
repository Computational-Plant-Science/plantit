import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class SubmissionConsumer(WebsocketConsumer):
    def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        print(f"Socket connected for user {self.username} submissions")
        async_to_sync(self.channel_layer.group_add)(f"submissions-{self.username}", self.channel_name)
        self.accept()

    def disconnect(self, code):
        print(f"Socket disconnected for user {self.username} submissions")
        async_to_sync(self.channel_layer.group_discard)(f"submissions-{self.username}", self.channel_name)

    def update_status(self, event):
        submission = event['submission']
        print(f"Sending websocket update for submission {submission['name']} with status {submission['status']}")
        self.send(text_data=json.dumps({
            'submission': submission,
        }))
