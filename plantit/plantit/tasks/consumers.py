import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class TaskConsumer(WebsocketConsumer):
    def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        print(f"Socket connected for user {self.username} tasks")
        async_to_sync(self.channel_layer.group_add)(f"tasks-{self.username}", self.channel_name)
        self.accept()

    def disconnect(self, code):
        print(f"Socket disconnected for user {self.username} tasks")
        async_to_sync(self.channel_layer.group_discard)(f"tasks-{self.username}", self.channel_name)

    def task_event(self, event):
        task = event['task']
        print(f"Sending websocket update for task {task['name']} with status {task['status']}")
        self.send(text_data=json.dumps({'task': task}))
