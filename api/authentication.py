from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.authentication import TokenAuthentication
from django.http import HttpResponse
from rest_framework import status

class ExpiringTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.get(key=key)
        except model.DoesNotExist:
            return HttpResponse(status = status.HTTP_405_METHOD_NOT_ALLOWED)

        return token.user, token
