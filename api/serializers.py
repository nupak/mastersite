from rest_framework import serializers
from main.models import news,scientist
from rest_framework.utils import model_meta
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import base64
User = get_user_model()
#Сериализаторы для новостей

class newsPreviewSerializer(serializers.ModelSerializer):
    """
        Список новостей
    """
    date = serializers.DateField(format='%d.%m')
    class Meta:
        model = news
        fields = [
            'id',
            'date',
            'headLine',
            'announce',
            'image',
        ]
#-------------------------------------------------------------
class newDetailSerializer(serializers.ModelSerializer):
    """
        Получение информации одной новости
    """
    date = serializers.DateField(format= '%d.%m')
    class Meta:
        model = news
        fields = [
            'headLine',
            'date',
            'text',
            'image'
        ]


class pointsListSerializer(serializers.ModelSerializer):
    """
        Сериализатор для точек
    """
    class Meta:
        model = scientist
        fields = [
            'id',
            'name',
            'patronymic',
            'surname',
            'Bigregion',
            'region',
            'ymapshortcut'
        ]


class profileUpdateDetailSerializer(serializers.ModelSerializer):
    """
            Сериализатор для обновления(редактирования)/получения страницы ученого
    """
    #user = serializers.HiddenField(default = serializers.CurrentUserDefault())
    def update(self, instance, validated_data):
        serializers.raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)


        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        instance.ymapshortcut = instance.getjsonShort2()
        print(instance.image)
        #if instance.image:
        this = scientist.objects.get(id=instance.id)
        #    print(this.image)
        #    if this.image != instance.image:
        #        this.image.delete(save=False)
        this.image = instance.image

        instance.save()


        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance

    class Meta:
        model = scientist
        exclude = ['password',
                   'date_joined',
                   'last_login',
                   'is_admin',
                   'is_active',
                   'is_staff',
                   'is_superuser',
                   #'ymapshortcut',
                   'keyWordsString',
                   'username'
        ]


#class AuthTokenSerializer(serializers.Serializer):
#    email = serializers.CharField(
#        label=_("email"),
#        write_only=True
#    )
#    password = serializers.CharField(
#        label=_("Password"),
#        style={'input_type': 'password'},
#        trim_whitespace=False,
#        write_only=True
#    )
#    token = serializers.CharField(
#        label=_("Token"),
#        read_only=True
#    )
#
#    def validate(self, attrs):
#        email = attrs.get('email')
#        password = attrs.get('password')
#
#        if email and password:
#            user = authenticate(request=self.context.get('request'),
#                                email=email, password=password)
#
#            # The authenticate call simply returns None for is_active=False
#            # users. (Assuming the default ModelBackend authentication
#            # backend.)
#            if not user:
#                msg = _('Unable to log in with provided credentials.')
#                raise serializers.ValidationError(msg, code='authorization')
#        else:
#            msg = _('Must include "username" and "password".')
#            raise serializers.ValidationError(msg, code='authorization')
#
#        attrs['user'] = user
#        return attrs

#    def update(self, instance, validated_data):
#        serializers.raise_errors_on_nested_writes('update', self, validated_data)
#        info = model_meta.get_field_info(instance)
#
#        m2m_fields = []
#        for attr, value in validated_data.items():
#            if attr in info.relations and info.relations[attr].to_many:
#                m2m_fields.append((attr, value))
#            else:
#                setattr(instance, attr, value)
#        instance.ymapshortcut = instance.getjsonShort()
#
#        instance.save()
#
#        for attr, value in m2m_fields:
#            field = getattr(instance, attr)
#            field.set(value)
#
#        return instance