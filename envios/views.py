from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Encomienda
from django.shortcuts import redirect
from django.contrib import messages
from .forms import EncomiendaForm


@login_required
def dashboard(request):
    total = Encomienda.objects.count()
    pendientes = Encomienda.objects.pendientes().count()
    activas = Encomienda.objects.activas().count()
    retraso = Encomienda.objects.con_retraso().count()

    return render(request, 'envios/dashboard.html', {
        'total': total,
        'pendientes': pendientes,
        'activas': activas,
        'retraso': retraso,
    })

@login_required
def perfil(request):
    """Vista del perfil del usuario"""
    user = request.user
    encomiendas_totales = Encomienda.objects.count()
    
    return render(request, 'perfil.html', {
        'user': user,
        'encomiendas_totales': encomiendas_totales,
    })

@login_required
def encomienda_lista(request):
    termino = request.GET.get('q', '').strip()

    encomiendas = Encomienda.objects.all()

    if termino:
        encomiendas = encomiendas.filter(
            Q(descripcion__icontains=termino) |
            Q(codigo__icontains=termino) |
            Q(remitente__nro_doc__icontains=termino) |
            Q(remitente__nombres__icontains=termino) |
            Q(remitente__apellidos__icontains=termino) |
            Q(destinatario__nro_doc__icontains=termino) |
            Q(destinatario__nombres__icontains=termino) |
            Q(destinatario__apellidos__icontains=termino)
        ).distinct()

    paginator = Paginator(encomiendas, 15)  # 👈 15 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'envios/lista.html', {
        'page_obj': page_obj,
        'termino': termino,
    })

@login_required
def encomienda_detalle(request, id):
    encomienda = get_object_or_404(Encomienda, id=id)

    historial = encomienda.historialestado_set.all()

    return render(request, 'envios/detalle.html', {
        'encomienda': encomienda,
        'historial': historial
    })

@login_required
def encomienda_crear(request):
    if request.method == 'POST':
        form = EncomiendaForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Encomienda creada correctamente")
            return redirect('encomienda_lista')
        else:
            messages.error(request, "Error al crear encomienda")
    else:
        form = EncomiendaForm()

    return render(request, 'envios/form.html', {
        'form': form
    })