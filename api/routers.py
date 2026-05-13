from rest_framework.permissions import AllowAny
from rest_framework.routers import APIRootView, DefaultRouter


class PublicAPIRootView(APIRootView):
    permission_classes = [AllowAny]


class PublicRootDefaultRouter(DefaultRouter):
    APIRootView = PublicAPIRootView
