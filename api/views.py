from .serializers import *
from .authentication import ExpiringTokenAuthentication


from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse,JsonResponse
from django.utils.timezone import utc
from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework import views
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from datetime import timedelta
from datetime import datetime
import pytz
from pytz import utc
import datetime
from scientistSite.settings import SITE_NAME, MEDIA_URL
from main.models import news, scientist
from chat.models import PrivateChatRoom

User = get_user_model()

class tokenchek(generics.RetrieveAPIView):
    """
        Проверка валидности токена
    """

    def get (self, request):
        key = request.headers.get('authorization')
        try:
            token=Token.objects.get(key=key)
        except Token.DoesNotExist:
            return HttpResponse(status = status.HTTP_403_FORBIDDEN)
        return HttpResponse(status=status.HTTP_200_OK)

class chek(generics.RetrieveAPIView):
    queryset = {}
    authentication_classes = (ExpiringTokenAuthentication, )

#===>  Вьюхи для новостей  <====
class NewsListSet(generics.ListAPIView):
    """
        Выдача списка новостей с параметрами page и size
    """
    serializer_class = newsPreviewSerializer

    def get_queryset(self):
        queryset = news.objects.all().order_by('-id')
        pageOfGet = self.request.query_params.get('page', None)
        if pageOfGet!=None:
             pageOfGet = int(pageOfGet)
        size = self.request.query_params.get('size', None)
        if size!=None:
             size = int(size)
        print(pageOfGet,size)
        if (pageOfGet or pageOfGet==0) and size:
            queryset = queryset[pageOfGet * size:(pageOfGet * size) + size]
        return queryset


class newsCount(views.APIView):
    """
        Поучение количества новостей
    """
    def get(self, request):
        counter = news.objects.count()

        return JsonResponse({'count':counter})


class NewDetailSet(generics.RetrieveAPIView):
    """
      Вывод для одной новости по ее индексу
    """
    queryset = news.objects.all().order_by('-id')
    serializer_class = newsPreviewSerializer


#===># Вьюхи для точек на карте  <====

class PointsListSet(generics.ListAPIView):
    """
        Получение списка ученых по данным с поиска для ЯКарты
    """
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['Bigregion', 'region', 'academicDegree', 'codeSpeciality']
    queryset = scientist.objects.all()
    serializer_class = pointsListSerializer

    def list(self, request, *args, **kwargs):
        """
            Фильтрация по ключевым словам
        """
        queryset = self.filter_queryset(self.get_queryset()).exclude(is_staff=True)
        words = request.query_params.getlist('keywords', None)
        print(words)
        if words:
            if words.count(';') >= 1:
                words = ';'.join(words)
            for word in words:
                queryset = (queryset.filter(keyWords__icontains=word.lower()))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


#===>#Вьюхи для личного кабинета <====

class profileDetailsUpdateSet(generics.RetrieveUpdateAPIView):
    """
        Получение/редактирование страницы исследователя
    """
    queryset = scientist.objects.all()
    serializer_class = profileUpdateDetailSerializer
    #permission_classes = (IsAuthenticated)
    authentication_classes = (ExpiringTokenAuthentication, )


class get_or_createСhatRoom(generics.CreateAPIView):
    """
        Создание комнаты чата
    """
    def post(self, request, *args, **kwargs):
        print(request.POST.get("user1_id"))
        user1 = request.POST.get("user1_id")
        user2 = request.POST.get("user2_id")
        print(user1)
        print(user2)
        if user1 == user2:
            return JsonResponse({'error':"нельзя создать чат с самим собой"})

        try:
            user1 = scientist.objects.get(pk=user1)
            user2 = scientist.objects.get(pk=user2)
        except:
            return JsonResponse({"error":"hav't user with this id"})

        try:
            print(PrivateChatRoom.objects.get(user1=user1, user2=user2))
            chat = PrivateChatRoom.objects.get(user1=user1, user2=user2)
        except PrivateChatRoom.DoesNotExist:
            try:
                print(PrivateChatRoom.objects.get(user1=user2, user2=user1))
                chat = PrivateChatRoom.objects.get(user1=user2, user2=user1)
            except PrivateChatRoom.DoesNotExist:
                chat = PrivateChatRoom(user1=user1, user2=user2)
                chat.save()
        print(user1,user2,chat.id)
        return JsonResponse({"room_id":chat.id})
#class profileCreateSet(generics.CreateAPIView):
#    """
#        Оставлю на будущее вдруг дорастем до автоматического создания аккаунтов
#    """
#    queryset = scientist.objects.all()
#    serializer_class = profileUpdateDetailSerializer
#    permission_classes = (IsAdminUser, )



class ObtainExpiringAuthToken2(ObtainAuthToken):
    """
        Переписал для login по почте и возврата больше инфы
    """
    def post(self,request):
        data = request.data
        try:
            email = data['email']
            password = data['password']
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email, password=password)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            token = Token.objects.get(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
            token.created = datetime.datetime.utcnow().replace(tzinfo=utc)
            token.save()
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        utc_now = utc_now.replace(tzinfo=pytz.utc)
        if token.created < utc_now - timedelta(hours=24):
            token.delete()
            token = Token.objects.create(user=user)
            token.created = datetime.datetime.utcnow().replace(tzinfo=utc)
            token.save()
        tokenkey = Token.objects.get(user=user).key
        fio=str(user.surname)+' '+str(user.name)+' '+str(user.patronymic)
        data = {'token': tokenkey,
                'pk':user.pk,
                'FIO':fio,
                'imagepath':SITE_NAME+MEDIA_URL+str((user.image))}
        print(data)
        return Response(data=data, status=status.HTTP_200_OK)


obtain_expiring_auth_token = ObtainExpiringAuthToken2.as_view()