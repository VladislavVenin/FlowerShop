from .models import Bouquet, Order
from .forms import ConsultationForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from more_itertools import chunked


def index(request):
    recommended = Bouquet.objects.filter(is_recommended=True)[:3]
    context = {
        'recommended': recommended,
    }
    return render(request, "index.html", context)


def catalog(request):
    bouquets = Bouquet.objects.filter(is_available=True)
    bouquets_in_row = list(chunked(bouquets, 3))
    context = {
        'rows': bouquets_in_row,
    }
    return render(request, "catalog.html", context)


def card(request, id):
    bouquet = get_object_or_404(Bouquet, id=id)
    flowers = bouquet.flowers.all()
    context = {
        'bouquet': bouquet,
        'flowers': flowers,
    }
    return render(request, "card.html", context)


def consultation(request):
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']

            Order.objects.create(
                client_name=name,
                phone_number=phone,
            )
            messages.success(request, f'Спасибо, {name}! Мы свяжемся с вами в ближайшее время.')
            return redirect('consultation')
        else:
            messages.error(request, 'Пожалуйста, проверьте правильность заполнения формы.')
            return render(request, 'consultation.html', {'form': form})
    form = ConsultationForm()
    return render(request, 'consultation.html', {'form': form})
