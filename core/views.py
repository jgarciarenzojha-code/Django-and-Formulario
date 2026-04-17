from django.shortcuts import render

from .forms import ContactForm


def home(request):
    success = False
    name = ''
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            success = True
            name = form.cleaned_data['name']
            form = ContactForm()
    else:
        form = ContactForm()

    return render(request, 'core/index.html', {
        'form': form,
        'success': success,
        'name': name,
    })
