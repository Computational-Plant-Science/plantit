from channels.generic.websocket import JsonWebsocketConsumer

from plantit.datasets.models import DatasetSession


class DatasetSessionConsumer(JsonWebsocketConsumer):
    def connect(self):
        try:
            self.guid = self.scope['url_route']['kwargs']['guid']
            session = DatasetSession.objects.get(guid=self.guid)
            session.channel_name = self.channel_name
            session.save()
            self.accept()
            print(f"Socket connected for dataset session {self.guid}")
        except:
            self.close()

    def disconnect(self, code):
        print(f"Socket disconnected for user dataset session {self.guid}")

    def update_session(self, event):
        session = event['session']
        print(f"Received dataset session {self.guid} update: {session}")
        self.send_json({
            'session': session
        })
