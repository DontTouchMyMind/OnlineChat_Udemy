from .base import BaseChatConsumer
from channels.db import database_sync_to_async
from chat.models import GroupParticipant, ChatGroup
from django.contrib.auth import get_user_model


class GroupChatConsumer(BaseChatConsumer):

    async def event_group_list(self, event):
        """Get a list of groups in which the user is located."""
        data = await self.group_list(self.scope['user'])
        await self._send_message(data, event=event['event'])

    async def event_user_list(self, event):
        """Get a list of users."""
        data = await self.user_list(self.scope['user'])
        await self._send_message(data, event=event['event'])

    async def event_group_create(self, event):
        """Group creation"""
        name = event['data'].get('name')
        if not name:
            return await self._throw_error({'detail': 'Missing group name!'}, event=event['event'])
        data = await self.group_create(name, self.scope['user'])
        await self._send_message(data, event=event['event'])

    @database_sync_to_async
    def group_list(self, user):
        group_ids = list(GroupParticipant.objects.filter(user=user).values_list('group', flat=True))
        result = []
        for group in ChatGroup.objects.filter(id__in=group_ids):
            result.append({
                'id': group.id,
                'name': group.name,
                'link': group.link,
            })
        return result

    @database_sync_to_async
    def user_list(self, user):
        users = get_user_model().objects.all().exclude(pk=user.id)
        result = []
        for user in users:
            result.append({
                'id': user.id,
                'username': user.username,
                'email': user.email
            })
        return result

    @database_sync_to_async
    def group_create(self, name, user):
        group = ChatGroup(name=name)
        group.save()
        participant = GroupParticipant(user=user, group=group)
        participant.save()
        return {
            'id': group.id,
            'name': group.name,
            'link': group.link
        }
