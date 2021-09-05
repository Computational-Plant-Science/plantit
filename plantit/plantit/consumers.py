import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class UserEventConsumer(WebsocketConsumer):
    logger = logging.getLogger(__name__)

    def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        self.logger.info(f"Socket connected for user {self.username}")
        async_to_sync(self.channel_layer.group_add)(f"{self.username}", self.channel_name)
        self.accept()

    def disconnect(self, code):
        self.logger.info(f"Socket disconnected for user {self.username}")
        async_to_sync(self.channel_layer.group_discard)(f"{self.username}", self.channel_name)

    def push_notification(self, event):
        notification = event['notification']
        self.logger.info(f"Received notification for user {self.username}: {notification}")
        self.send(text_data=json.dumps({
            'notification': notification,
        }))

    def task_log_event(self, event):
        task = event['task']
        logs = event['logs']
        self.logger.info(f"Sending user {self.username} task {task['name']} log event (status {task['status']}) to client ({len(logs)} lines)")
        self.send(text_data=json.dumps({'logs': logs}))

    def task_event(self, event):
        task = event['task']
        self.logger.info(f"Sending user {self.username} task {task['name']} event (status {task['status']}) to client")
        self.send(text_data=json.dumps({'task': task}))