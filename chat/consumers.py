import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, JsonWebsocketConsumer, \
    AsyncJsonWebsocketConsumer
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async
from .models import Online


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()  # Установка соединения

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        i = 0
        for header in self.scope['headers']:
            print(f'Header №{i}: {header[0]} have {header[1]}')
            i += 1
            print('-' * 25)
        print(f'URL_ROUTE: {self.scope["url_route"]}')
        print(f'PATH: {self.scope["path"]}')

        json_data = json.loads(text_data)
        message = json_data['message']

        self.send(text_data=json.dumps({
            'message': message
        }))


class AsyncChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()  # Установка соединения.

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        json_data = json.loads(text_data)
        message = json_data['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))


class BaseSyncConsumer(SyncConsumer):

    def websocket_connect(self, event):  # Event - dict, first key is 'type'.
        # Всего несколько методов websocket.accept, websocket.send, websocket.disconnect, websocket.receive.
        # Аналог self.accept().
        print('Connecting')
        self.send({
            'type': 'websocket.accept'
        })

    def websocket_receive(self, event):
        self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    def websocket_disconnect(self):
        raise StopConsumer()


class AsyncBaseSyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })


class ChatJsonConsumer(JsonWebsocketConsumer):

    def connect(self):
        self.accept()  # Установка соединения

    def disconnect(self, code):
        pass

    def receive_json(self, content, **kwargs):
        self.send_json(content=content)

    @classmethod
    def decode_json(cls, text_data):
        return super().decode_json(text_data)

    @classmethod
    def encode_json(cls, content):
        return super().encode_json(content)


class ChatAsyncJsonConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive_json(self, content, **kwargs):
        await self.send_json(content=content)

    @classmethod
    async def decode_json(cls, text_data):
        return await super().decode_json(text_data)

    @classmethod
    async def encode_json(cls, content):
        return await super().encode_json(content)


class MyChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,
            {
                'type': 'chat.message',
                'text': text_data
            }
        )

    def chat_message(self, event):
        self.send(text_data=event['text'])


class MyAsyncChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        await self.create_online()

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        self.scope['session']['my_var'] = 'Hello. Its my var!'
        await database_sync_to_async(self.scope['session'].save)()
        await self.accept()

    async def disconnect(self, code):
        await self.delete_online()
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        await self.refresh_online()
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat.message',
                'text': self.scope['session']['my_var']
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=event['text'])

    @database_sync_to_async
    def create_online(self):
        new, _ = Online.objects.get_or_create(name=self.channel_name)
        self.online = new

    @database_sync_to_async
    def delete_online(self):
        Online.objects.filter(name=self.channel_name).delete()

    @database_sync_to_async
    def refresh_online(self):
        self.online.refresh_from_db()
