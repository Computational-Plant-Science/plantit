import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from plantit.runs.models import Run
from plantit.runs.utils import map_run


class RunConsumer(WebsocketConsumer):
    def connect(self):
        self.username = self.scope['url_route']['kwargs']['username']
        print(f"Socket connected for user {self.username} notifications")
        async_to_sync(self.channel_layer.group_add)(f"runs-{self.username}", self.channel_name)
        self.accept()

    def disconnect(self, code):
        print(f"Socket disconnected for user {self.username} runs")
        async_to_sync(self.channel_layer.group_discard)(f"runs-{self.username}", self.channel_name)

    def update_status(self, event):
        run = event['run']
        print(f"Received status update for run {run['id']} with status {run['job_status']}")
        self.send(text_data=json.dumps({
            'run': run,
        }))
