from django.urls import path
from .views import encomienda_lista, encomienda_detalle, encomienda_crear, dashboard, perfil

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('perfil/', perfil, name='perfil'),
    path('encomiendas/', encomienda_lista, name='encomienda_lista'),
    path('encomiendas/<int:id>/', encomienda_detalle, name='encomienda_detalle'),
    path('encomiendas/nuevo/', encomienda_crear, name='encomienda_crear'),
]