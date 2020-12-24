from django.shortcuts import render
from itertools import chain

from chat.models import PrivateChatRoom,RoomChatMessage


"""
def private_chat_room_view(request, *args, **kwargs):
from chat.utils import find_or_create_private_chat

    user=request.user

    if not user.is_authenticated:
        return HttpResponse (403)

    rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active = True)
    rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active = True)

    rooms = list(chain(rooms1,rooms2))
    mes_and_f=[]
    for room in rooms:
        if room.user1 == user:
            friend = room.user2
        else:
            friend = rooms.user1
        mes_and_f.append({
            'message':'',
            'friend':friend
        })
    return JsonResponse

def create_or_return_private_chat(request, *args, **kwargs):
    user1 = request.user
    payload = {}
    if user1.is_authenticated:
        if request.method == 'POST':
            user2_id = request.POST.get('user2_id')
            try:
                user2 = User.objects.get(pk=user2_id)
                chat = find_or_create_private_chat

"""