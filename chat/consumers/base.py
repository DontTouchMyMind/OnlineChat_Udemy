from channels.generic.websocket import AsyncJsonWebsocketConsumer


class BaseChatConsumer(AsyncJsonWebsocketConsumer):
    async def _group_send(self, data, event=None):
        # Create a message that we will send to the channel layers.
        data = {'type': 'response.proxy', 'data': data, 'event': event}
        # The message will be send with 'response_proxy' method.
        await self.channel_layer.group_send(self.channel, data)

    async def response_proxy(self, event):
        await self._send_message(event['data'], event=event.get('event'))

    async def _send_message(self, data, event=None):
        await self.send_json(content={'status': 'ok',
                                      'data': data,
                                      'event': event})

    async def _throw_error(self, data, event=None):
        await self.send_json(content={'status': 'error',
                                      'data': data,
                                      'event': event})

    async def connect(self):
        await self.accept()
        # if the user is not logged in.
        if 'user' not in self.scope or self.scope['user'].is_anonymous:
            # Send error-message on client.
            await self._send_message({'detail': 'Authorization failed!'})  # Or call _throw_error?
            # Disconnect.
            await self.close(code=1000)
            return

    async def receive_json(self, content, **kwargs):
        message = await self.parse_content(content)
        if message:
            event = message['event'].replace('.', '_')
            # We get object self, and find in it 'event_{event}'.
            # If event is not find, we will call handler 'method_undefined'.
            method = getattr(self, f'event_{event}', self.method_undefined)
            # Pass the entire object received form the client to the method.
            await method(message)
        else:
            # Send error-message to the client, if message is not valid.
            await self._throw_error({'detail': 'Invalid message!'})

    async def method_undefined(self, message):
        # Send to client message 'Unknown event'.
        await self._throw_error({'detail': 'Unknown event'}, event=message['event'])

    @classmethod
    async def parse_content(cls, content):
        """
        The function checks if the message is valid.
        :param content:
        :return:
        """
        if isinstance(content, dict) and isinstance(content.get('event'), str) \
                and isinstance(content.get('data'), dict):
            return content
