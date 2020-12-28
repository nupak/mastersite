from datetime import datetime
from django.contrib.humanize.templatetags.humanize import naturalday
from django.core.serializers.python import Serializer

from chat.models import PrivateChatRoom
from scientistSite.settings import SITE_NAME


def find_or_create_private_chat(user1, user2):
	try:
		chat = PrivateChatRoom.objects.get(user1=user1, user2=user2)
	except PrivateChatRoom.DoesNotExist:
		try:
			chat = PrivateChatRoom.objects.get(user1=user2, user2=user1)
		except PrivateChatRoom.DoesNotExist:
			chat = PrivateChatRoom(user1=user1, user2=user2)
			chat.save()
	return chat


def calculate_timestamp(timestamp):
	"""
	1. Today or yesterday:
		- EX: 'today at 10:56 AM'
		- EX: 'yesterday at 5:19 PM'
	2. other:
		- EX: 05/06/2020
		- EX: 12/28/2020
	"""
	ts = ""
	# Today or yesterday
	if str((naturalday(timestamp)) == "сегодня") or str((naturalday(timestamp)) == "вчера"):
		str_time = datetime.strftime(timestamp, "%I:%M")
		str_time = str_time.strip("0")
		ts = f"{naturalday(timestamp)} at {str_time}"
	# other days
	else:
		str_time = datetime.strftime(timestamp, "%d/%m/%Y")
		ts = f"{str_time}"
	return str(ts)


"""
Аналог сериализтора для выдачи сообщений
"""

class LazyRoomChatMessageEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'msg_id': str(obj.id)})
        dump_object.update({'user_id': str(obj.user.id)})
        dump_object.update({'username': str(obj.user.name)})
        dump_object.update({'message': str(obj.content)})
        dump_object.update({'profile_image': SITE_NAME+str(obj.user.image.url)})
        dump_object.update({'natural_timestamp': str(obj.timestamp)})
        return dump_object

