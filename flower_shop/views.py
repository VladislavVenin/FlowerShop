from .models import Bouquet, Order, Event
from .forms import ConsultationForm


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from more_itertools import chunked
from django.db.models import Prefetch


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


def quiz(request):
    #тут цикл из событий
    if request.method == 'POST':
        event = request.POST.get('event')
        request.session['quiz'] = {'event': event}
        request.session.modified = True
        return redirect('quiz_step')

    events = Event.objects.all().values("id", "name")
    return render(request, 'quiz.html', {'events': events})

def quiz_step(request):
    if request.method == 'POST':
        price = request.POST.get('price')
        quiz_data = request.session.get('quiz', {})
        quiz_data['price'] = price
        request.session['quiz'] = quiz_data
        request.session.modified = True
        return redirect('result')
    return render(request, 'quiz-step.html')


def result(request):
    data = request.session.get('quiz')
    event_id = data['event']
    price_id =data['price']

    bouquets_query = Bouquet.objects.all()

    match price_id:
        case '1':
            cost_filtered = bouquets_query.filter(price__lt=1000)
        case '2':
            cost_filtered = bouquets_query.filter(price__range=(1000, 5000))
        case '3':
            cost_filtered = bouquets_query.filter(price__gt=5000)
        case '4':
            cost_filtered = bouquets_query
        case _:
            cost_filtered = bouquets_query

    if not cost_filtered.exists():
        cost_filtered = Bouquet.objects.all()

    event_filtered = cost_filtered.filter(events__id=event_id).distinct()

    if not event_filtered.exists():
        final_filtered = cost_filtered
    else:
        final_filtered = event_filtered

    bouquet_flowers_prefetch = Prefetch(
        'bouquetflower_set',
        queryset=Bouquet.objects.select_related('flower'),
        to_attr='flower_items'
    )

    final_bouquets = final_filtered.prefetch_related(
        bouquet_flowers_prefetch,
    )

    bouquet_list = []
    for bouquet in final_bouquets:
        flowers_lines = [
            f"{bf.flower.name} - {bf.quantity} шт."
            for bf in bouquet.bouquetflower_set.all()
        ]
        all_lines = flowers_lines
        full_composition = "\n".join(all_lines) + "\n"
        bouquet_data = {
            "id": bouquet.id,
            "name": bouquet.name,
            "flowers": full_composition,
            "price": int(bouquet.price),
            "width": float(bouquet.width),
            "height": float(bouquet.length),
            "img": bouquet.image.url if bouquet.image else "",
            "description": bouquet.description
        }
        bouquet_list.append(bouquet_data)

    selected_bouquet = random.choice(bouquet_list) if bouquet_list else None
    return render(request, 'result.html', {"bouquet": selected_bouquet})