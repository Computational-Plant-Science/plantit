import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from plantit.runs.models import Run
from plantit.runs.utils import map_run


class RunConsumer(WebsocketConsumer):
    def connect(self):
        self.run_id = self.scope['url_route']['kwargs']['id']
        print(f"Socket connected for run {self.run_id}")
        async_to_sync(self.channel_layer.group_add)(self.run_id, self.channel_name)
        self.accept()

    def disconnect(self, code):
        print(f"Socket disconnected for run {self.run_id}")
        async_to_sync(self.channel_layer.group_discard)(self.run_id, self.channel_name)

    def update_status(self, event):
        run = Run.objects.get(guid=self.run_id)
        print(f"Received status update for run {self.run_id} with status {run.job_status}")
        self.send(text_data=json.dumps({
            'run': map_run(run, True),
        }))
