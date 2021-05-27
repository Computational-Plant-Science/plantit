import json
import logging

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

logger = logging.getLogger(__name__)


class WorkflowConsumer(WebsocketConsumer):
    def connect(self):
        self.owner = self.scope['url_route']['kwargs']['owner']
        logger.info(f"Socket connected for {self.owner}'s workflows")
        async_to_sync(self.channel_layer.group_add)(f"workflows-{self.owner}", self.channel_name)
        self.accept()

    def disconnect(self, code):
        logger.info(f"Socket disconnected for {self.owner}'s workflows")
        async_to_sync(self.channel_layer.group_discard)(f"workflows-{self.owner}", self.channel_name)

    def update_workflow(self, event):
        workflow = event['workflow']
        logger.info(f"Pushing {self.owner}'s workflow {workflow['repo']['name']} add/update to client")
        self.send(text_data=json.dumps({
            'operation': 'update',
            'workflow': workflow
        }))

    def remove_workflow(self, event):
        workflow = event['workflow']
        logger.info(f"Pushing {self.owner}'s workflow {workflow['repo']['name']} removal to client")
        self.send(text_data=json.dumps({
            'operation': 'remove',
            'workflow': workflow
        }))
