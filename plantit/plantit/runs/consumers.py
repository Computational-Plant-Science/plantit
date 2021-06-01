import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class RunConsumer(WebsocketConsumer):
    def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        print(f"Socket connected for user {self.username} runs")
        async_to_sync(self.channel_layer.group_add)(f"runs-{self.username}", self.channel_name)
        self.accept()

    def disconnect(self, code):
        print(f"Socket disconnected for user {self.username} runs")
        async_to_sync(self.channel_layer.group_discard)(f"runs-{self.username}", self.channel_name)

    def update_status(self, event):
        run = event['run']
        print(f"Sending websocket update for run {run['name']} with status {run['job_status']}")
        self.send(text_data=json.dumps({
            'run': run,
        }))
