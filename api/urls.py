from django.conf import settings
from django.contrib import admin
from django.urls import path


#internals
from api.views import CodeExplainerView, TokenView, UserView

urlpatterns = [
    path("users/", UserView.as_view(), name="users"),
    path("tokens/", TokenView.as_view(), name="tokens"),
    path('code-explain/' CodeExplainerView.as_view(), name='code-explain'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
