from .models import Bouquet

from django.shortcuts import render, get_object_or_404
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
    return render(request, "consultation.html")