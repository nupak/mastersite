from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize
from django.utils import timezone
from django.core.paginator import Paginator
from itertools import chain
import json
import asyncio

from chat.models import RoomChatMessage, PrivateChatRoom  # , UnreadChatRoomMessages
# from account.utils import LazyAccountEncoder
from chat.utils import *
from chat.exceptions import ClientError
# from chat.constants import *
from main.models import scientist
from scientistSite.settings import SITE_NAME


def scope_to_str(scope):
    res = '******* Scope ********* \n'
    headers = scope.pop('headers', None)
    for k, v in scope.items():
        res += f"{k} - {v} \n"
    res += "======== Headers =========\n"
    for k, v in headers:
        res += f"{k} - {v}\n"
    res += "******* End Scope ********\n"
    return res


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def _send_message(self, data, event=None):
        await self.send_json(content={"status": "ok", "data": data, "event": event})

    async def _throw_error(self, data, event=None):
        await self.send_json(content={"status": "error", "data": data, "event": event})

    async def connect(self):
        """
        Подключение вэб сокета
        """
        #print("ChatConsumer: connect: " + str(self.scope["user"]))
        await self.accept()
        #if 'user' not in self.scope or self.scope['user'].is_anonymous:
        #    await self._send_message({"detail": "Пользователь не авторизован"})
        #    await self.close(1000)
        #    return
        print("Есть коннект")
        # Если пользоватеьл в комнате рум айди не пустой
        self.room_id = None


    #async def disconnect(self, code):
       #print('Hi))')

    async def receive_json(self, content):
        """
            Обработка комманд с клиента
        """
        # Внутри Json должно быть поле command
        print("ChatConsumer: receive_json")
        command = content.get("command", None)
        print(command)
        try:
            if command == "join":
                # Подключение в комнату
                #print("joining room: " + str(content['room']))
                await self.join_room(content["room"])
            elif command == "leave":
                # Отключение из комнаты
                await self.leave_room(content["room"])
            elif command == "send":
                if len(content["message"].lstrip()) == 0:
                    raise ClientError(422, "Нельзя отправить пустое сообщение")
                await self.send_room(content["room"], content["message"])
            elif command == "get_room_chat_messages":
                #print(content)
                room = await get_room_or_error(content['room'], self.scope["user"])
                #print(room)
                payload = await get_room_chat_messages(room, content['pagenumber'])
                if payload != None:
                    payload = json.loads(payload)
                    await self.send_messages_payload(payload['messages'], payload['new_page_number'])
                else:
                    raise ClientError(204, "Something went wrong retrieving the chatroom messages.")
                print(payload)
            elif command == "setuser":
                print(content)
                try:
                    user_id = content["user_id"]
                    user = await get_user(user_id)
                    self.scope["user"] = user
                    #print("Установлен Юзверь "+self.scope['user'].username)
                except:
                    print("No user ID")

        except Exception as e:
            print(str(Exception),e)

# Реализация команд
    async def join_room(self, room_id):
        """
               Команда join:подключение к комнате
        """
        #print("ChatConsumer: join_room: " + str(room_id))
        try:
            room = await get_room_or_error(room_id, self.scope["user"])
        except ClientError as e:
            return await self.handle_client_error(e)

        # Добавление человека в список онлйан пользователей
        #await connect_user(room, self.scope["user"])

        # Подтверждаем что мы в комнате
        self.room_id = room.id

        #Очитска непрочитанных сообщений
        #await on_user_connected(room, self.scope["user"])

        #Добавление в комнату чата дял получения сообщения(активация подписки)
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )
        #print(room.group_name)
        #print(self.channel_name)
        #print("----------")
        # Подтверждения для клиента завершения входа в комнату
        await self.send_json({
            "join": str(self),
        })

    async def leave_room(self, room_id):
        """
            Команда  leave отключение выхода человека из комнаты чата и статус офлайн
        """
        print("ChatConsumer: leave_room")

        room = await get_room_or_error(room_id, self.scope["user"])

        # Удаляем пользователя из списка онлайн чата
        await disconnect_user(room, self.scope["user"])

        # Удаления статуса подключение к комнате
        self.room_id = None

        # Отключение подписка на получение данных из комнаты
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )
        # Подтверждение выхода из комнаты для клиента
        await self.send_json({
            "leave": str(room.id),
        })

    async def send_room(self, room_id, message):
        """
            Отправка сообщения в комнату
        """
        #print("ChatConsumer: send_room")
        # Проверка подключения к комнате
        if self.room_id != None:
            if str(room_id) != str(self.room_id):
                print("User in other chat")
                raise ClientError("ROOM_ACCESS_DENIED", "Error room connecting")
        else:
            print("CLIENT ERRROR 2")
            raise ClientError("ROOM_ACCESS_DENIED", "User not connected to room")

        # Получение данных комнаты
        room = await get_room_or_error(room_id, self.scope["user"])

        # Получения списка онлайн пользователей
        #connected_users = room.connected_users.all()

        # Execute these functions asychronously ?!?!
        await asyncio.gather(*[
            #append_unread_msg_if_not_connected(room, room.user1, connected_users, message),
            #append_unread_msg_if_not_connected(room, room.user2, connected_users, message),
            create_room_chat_message(room, self.scope["user"], message)
        ])
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "username": self.scope["user"].name,
                "user_id": self.scope["user"].id,
                "message": message,
            }
        )
        self.scope["user"]
        await roomlistConsumer.send_list(self.scope["user"])


    async def chat_message(self, event):
       """
       Called when someone has messaged our chat.
       """
       # Send a message down to the client


       timestamp = str(timezone.now())
       await self.send_json(
           {
               "command":"send",
               "username": event["username"],
               "user_id": event["user_id"],
               "message": event["message"],
               "natural_timestamp": timestamp,
           },
       )

    async def send_messages_payload(self, messages, new_page_number):
        """
        Send a payload of messages to the ui
        """
        print("ChatConsumer: send_messages_payload. ")
        await self.send_json(
            {   "command":"get_room_chat_messages",
                "messages_payload": "messages_payload",
                "messages": messages,
                "new_page_number": new_page_number,
            },
        )



    async def handle_client_error(self, e):
        """
            Отправка ошибки на клиент когда срабатывает эксепшн
        """
        errorData = {}
        errorData['error'] = e.code
        if e.message:
            errorData['message'] = e.message
            await self.send_json(errorData)
        return


class roomlistConsumer(AsyncJsonWebsocketConsumer):
    """
        Получения списка комнат чата
    """

    async def _send_message(self, data, event=None):
        await self.send_json(content={"command": "get_list", "data": data, "event": event})

    async def _throw_error(self, data, event=None):
        await self.send_json(content={"status": "error", "data": data, "event": event})

    async def connect(self):
        """
        Подключение вэб сокета cообщений
        """

        await self.accept()

        #print("Есть коннект к листу")

        # Если пользоватеьл в комнате рум айди не пустой

    async def receive_json(self, content):
        """
            Обработка комманд с клиента
        """
        # Внутри Json должно быть поле command
        #print("ChatConsumer: receive_json")
        command = content.get("command", None)
        #print(command)
        if command == "setuser":
            user_id = content["user_id"]
            user = await get_user(user_id)
            self.scope["user"] = user
            print("Лист пользователя " + self.scope['user'].username)
        elif command == "get_list":
            user = self.scope['user']
            print(user)
            await self.send_list(user)

    async def send_list(self,user):
        """
         Отправка листа диалогов
        """
        m_f = await get_room_list(user)
        print(m_f)
        print("Ready list")
        if m_f==[]:
            await self.send_json({"command":"error",
                                  "content":"User has't rooms"})
        else:
            m_f = {"command": "get_list", "roomlist": m_f}
            await self.send_json(m_f)




"""
Создание сообщения в бд
"""
@database_sync_to_async
def create_room_chat_message(room, user, message):
    return RoomChatMessage.objects.create(user=user, room=room, content=message)

@database_sync_to_async
def get_user(user_id):
    return (scientist.objects.get(pk=user_id))

@database_sync_to_async
def connect_user(room, user):
    # добавляет пользователя в список Онлайн пользователей чата
    account = scientist.objects.get(pk=user.id)
    return room.connect_user(account)

@database_sync_to_async
def disconnect_user(room, user):
    # Удаление из списка онлайн
    account = scientist.objects.get(pk=user.id)
    return room.disconnect_user(account)

@database_sync_to_async
def get_room_or_error(room_id, user):
    """
        Получение комнаты и проверка что пользователь участник чата

    """
    try:
        room = PrivateChatRoom.objects.get(pk=room_id)
    except PrivateChatRoom.DoesNotExist:
        raise ClientError("ROOM_INVALID", "Invalid room.")

    # Is this user allowed in the room? (must be user1 or user2)
    if (str(user.username) != str(room.user1)) and (str(user.username) != str(room.user2)):
        raise ClientError("ROOM_ACCESS_DENIED", "You do not have permission to join this room.")

    return room

@database_sync_to_async
def get_room_chat_messages(room, page_number):
    #print(room, page_number)
    try:
        qs = RoomChatMessage.objects.by_room(room)
        #p = Paginator(qs, 10)

        payload = {}
        messages_data = None
        new_page_number = int(page_number)
        s = LazyRoomChatMessageEncoder()

        payload['messages'] = s.serialize(qs)
        payload['new_page_number'] = new_page_number
        #print(payload)
        return json.dumps(payload)
    except Exception as e:
        print("EXCEPTION: " + str(e))
    return None

@database_sync_to_async
def getuser_by_id(user_id):
    try:
        user = scientist.objects.get(pk=user_id)
        return user
    except:
        print("Unnown user")


@database_sync_to_async
def get_room_list(user):

    #rooms1 = list(PrivateChatRoom.objects.filter(user1=user, is_active = True))
    #rooms2 = list (PrivateChatRoom.objects.filter(user2=user, is_active = True))
    #rooms = rooms1
    #rooms.append(rooms2)
    #print(rooms)
    mes_and_f = []
    try:
        rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
        rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)
        rooms = list(chain(rooms1, rooms2))
    except:
        return mes_and_f
    if rooms:
        for room in rooms:
            if str(room.user1) == str(user):
                friend = room.user2
            else:
                friend = room.user1
            mes = RoomChatMessage.objects.get_mes_by_room(room)
            if mes:
                print("mes:",mes)
                mes_and_f.append({
                    'command':'get_list',
                    'friend_id':friend.id,
                    "friend_photo":SITE_NAME+str(friend.image.url),
                    "friend_name":friend.name,
                    "friend_surname": friend.surname,
                    "room_id": room.pk,
                    "last_message": mes.content,
                    "timestamp": str(mes.timestamp),
                    "mes_id": mes.pk
                })
            else:
                mes_and_f.append({
                    'command': 'get_list',
                    'friend_id': friend.id,
                    "friend_photo": SITE_NAME + str(friend.image.url),
                    "friend_name": friend.name,
                    "friend_surname": friend.surname,
                    "room_id": room.pk,
                    "last_message": "Нет сообщений"
                })

    return mes_and_f


# When a user connects, reset their unread message count
#@database_sync_to_async
#def on_user_connected(room, user):
#	# confirm they are in the connected users list
#	connected_users = room.connected_users.all()
#	if user in connected_users:
#		try:
#			# reset count
#			unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
#			unread_msgs.count = 0
#			unread_msgs.save()
#		except UnreadChatRoomMessages.DoesNotExist:
#			UnreadChatRoomMessages(room=room, user=user).save()
#			pass
#	return