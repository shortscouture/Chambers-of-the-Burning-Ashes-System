from django.conf import settings
from django.contrib import admin
from django.urls import path


#internals
from api.views import CodeExplainView, TokenView, UserView

urlpatterns = [
    #path("users/", UserView.as_view(), name="users"),
    #path("tokens/", TokenView.as_view(), name="tokens"),
    path("code-explain/", CodeExplainView.as_view(), name="code-explain"),
]
