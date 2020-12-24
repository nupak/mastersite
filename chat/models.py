from django.db import models
from django.conf import settings

class PrivateChatRoom(models.Model):

    """
    Приватный чат между 2 пользователями
    """

    user1            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name='user1')
    user2            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name='user2')
    is_active        = models.BooleanField(default=True)

    def __str__(self):
        return f"Чат между {self.user1} и {self.user2}"

    @property
    def group_name(self):
        """
        Возвращает имя канала, на который сокеты должны
        подписаться, чтобы они отправляли сообщение по мере их создания
        """
        return f"PrivateChatRoom-{self.id}"


class RoomChatMessageManager(models.Manager):
    def by_room(self,room):
        try:
            qs = RoomChatMessage.objects.filter(room__id=room.id).order_by('-timestamp')
        except:
            qs=[]
        return qs

    def get_mes_by_room(self, room):
        try:
            qs = RoomChatMessage.objects.filter(room__id=room.id).order_by('-timestamp')[0]
        except IndexError:
            qs=[]
        return qs


class RoomChatMessage(models.Model):
    '''
    Сообщения чата
    '''
    user        =models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room        =models.ForeignKey(PrivateChatRoom,on_delete=models.CASCADE)
    timestamp   =models.DateTimeField(auto_now_add=True)
    content     =models.TextField(unique=False,blank=False)

    objects = RoomChatMessageManager()

    def __str__(self):
        return  self.content
