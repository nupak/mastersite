
from django.urls import path
from api.views import *

urlpatterns = [
    path('news/all/',NewsListSet.as_view()),  #GET запроc с параметрами (page,size)/Получение списка новостей
    path('news/<int:pk>/',NewDetailSet.as_view()), # GET запрос/Получение полной новости
    path('news/count/',newsCount.as_view()),
    path('scientistprofile/<int:pk>/',profileDetailsUpdateSet.as_view()),  #Get запрос и  Patch запрос по каждому ученому Авторизация по обычному токену и с аутентификацией
    path('getpoints/',PointsListSet.as_view()), #GET Получение точек для карты  запрос с параметрами поиска, пока что выводятся все
    path('auth_token/token/tokenchek/', tokenchek.as_view()),  #GET Проверка валидности токена
    path('auth_token/token/login/', obtain_expiring_auth_token),  #POST Получение токена  body: email password
    path('createChatRoom/', get_or_createСhatRoom.as_view()), #Пусть создание новой комнаты чата
    #path('scientistprofile/create/', profileCreateSet.as_view()), Пусть будет на будущее, использовал только во время разработки Post запрос
    ]
