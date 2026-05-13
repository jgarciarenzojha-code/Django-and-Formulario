from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .routers import PublicRootDefaultRouter
from .views import (
    ClienteViewSet,
    CustomTokenObtainPairView,
    EmpleadoViewSet,
    EncomiendaAPIView,
    EncomiendaDetailAPIView,
    EncomiendaListCreateAPIView,
    EncomiendaMixinView,
    EncomiendaRetrieveUpdateDestroyAPIView,
    EncomiendaV2ViewSet,
    RutaViewSet,
    encomienda_fbv_detail,
    encomienda_fbv_list,
)


router = PublicRootDefaultRouter()
router.register(r'encomiendas', EncomiendaV2ViewSet, basename='encomiendas')
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'rutas', RutaViewSet, basename='rutas')
router.register(r'empleados', EmpleadoViewSet, basename='empleados')

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('schema/', SpectacularAPIView.as_view(api_version='v2'), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('fbv/encomiendas/', encomienda_fbv_list, name='fbv-encomienda-list'),
    path('fbv/encomiendas/<int:pk>/', encomienda_fbv_detail, name='fbv-encomienda-detail'),

    path('apiview/encomiendas/', EncomiendaAPIView.as_view(), name='apiview-encomienda-list'),
    path('apiview/encomiendas/<int:pk>/', EncomiendaDetailAPIView.as_view(), name='apiview-encomienda-detail'),

    path('mixins/encomiendas/', EncomiendaMixinView.as_view(), name='mixins-encomienda-list'),
    path('mixins/encomiendas/<int:pk>/', EncomiendaMixinView.as_view(), name='mixins-encomienda-detail'),

    path('generics/encomiendas/', EncomiendaListCreateAPIView.as_view(), name='generics-encomienda-list'),
    path(
        'generics/encomiendas/<int:pk>/',
        EncomiendaRetrieveUpdateDestroyAPIView.as_view(),
        name='generics-encomienda-detail',
    ),

    path('', include(router.urls)),
]
