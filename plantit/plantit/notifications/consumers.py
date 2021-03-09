import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        print(f"Socket connected for user {self.username} notifications")
        async_to_sync(self.channel_layer.group_add)(f"notifications-{self.username}", self.channel_name)
        self.accept()

    def disconnect(self, code):
        print(f"Socket disconnected for user {self.username} notifications")
        async_to_sync(self.channel_layer.group_discard)(f"notifications-{self.username}", self.channel_name)

    def push_notification(self, event):
        notification = event['notification']
        print(f"Received notification for user {self.username}: {notification}")
        self.send(text_data=json.dumps({
            'notification': notification,
        }))