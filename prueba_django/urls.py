from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [

    path('admin/', admin.site.urls),

    path('', include('envios.urls')),


    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='login.html',
            next_page='dashboard'
        ),
        name='login'
    ),

    path(
        'logout/',
        auth_views.LogoutView.as_view(
            next_page='login'
        ),
        name='logout'
    ),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/schema/', RedirectView.as_view(pattern_name='schema', permanent=False)),
    path('api/v1/docs/', RedirectView.as_view(pattern_name='swagger-ui', permanent=False)),
    path('api/v2/schema/', RedirectView.as_view(pattern_name='schema', permanent=False)),
    path('api/v2/docs/', RedirectView.as_view(pattern_name='swagger-ui', permanent=False)),
    path('api/v1/', include(('api.urls', 'api'), namespace='v1')),
    path('api/v2/', include(('api.urls_v2', 'api_v2'), namespace='v2')),
]
