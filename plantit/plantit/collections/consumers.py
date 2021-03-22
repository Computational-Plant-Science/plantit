from channels.generic.websocket import JsonWebsocketConsumer

from plantit.collections.models import CollectionSession


class CollectionSessionConsumer(JsonWebsocketConsumer):
    def connect(self):
        try:
            self.guid = self.scope['url_route']['kwargs']['guid']
            session = CollectionSession.objects.get(guid=self.guid)
            session.channel_name = self.channel_name
            session.save()
            self.accept()
            print(f"Socket connected for collection session {self.guid}")
        except:
            self.close()

    def disconnect(self, code):
        print(f"Socket disconnected for user collection session {self.guid}")

    def update_session(self, event):
        session = event['session']
        print(f"Received collection session {self.guid} update: {session}")
        self.send_json({
            'session': session
        })
        # await self.send(text_data=json.dumps({
        #     'session': session,
        # }))
