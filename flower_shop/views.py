import random
from datetime import time

from django.contrib import messages
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from more_itertools import chunked

from .forms import ConsultationForm
from .models import Bouquet, Event, Order
from .payment import create_payment, yookassa_webhook
from .utils import get_available_slots


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
            return redirect(request.META.get('HTTP_REFERER', 'consultation'))
        else:
            messages.error(request, 'Пожалуйста, проверьте правильность заполнения формы.')
            if request.META.get('HTTP_REFERER'):
                return redirect(request.META.get('HTTP_REFERER'))
            return render(request, 'consultation.html', {'form': form})
    form = ConsultationForm()
    return render(request, 'consultation.html', {'form': form})


def quiz(request):
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
    
    if not data:
        return redirect('quiz')  

    event_id = data.get('event')
    price_id = data.get('price')

    bouquets_query = Bouquet.objects.all()


    if price_id == '1':
        cost_filtered = bouquets_query.filter(price__lt=1000)
    elif price_id == '2':
        cost_filtered = bouquets_query.filter(price__range=(1000, 5000))
    elif price_id == '3':
        cost_filtered = bouquets_query.filter(price__gt=5000)
    else:
        cost_filtered = bouquets_query


    if not cost_filtered.exists():
        cost_filtered = Bouquet.objects.all()

    event_filtered = cost_filtered.filter(events__id=event_id).distinct()

    final_filtered = event_filtered if event_filtered.exists() else cost_filtered

    bouquet_list = []
    for bouquet in final_filtered:
        bouquet_data = {
            "id": bouquet.id,
            "name": bouquet.name,
            "price": float(bouquet.price),  
            "width": float(bouquet.width),
            "height": float(bouquet.height),
            "img": bouquet.image.url if bouquet.image else "",
            "description": bouquet.description,
            "flowers": ", ".join([flower.name for flower in bouquet.flowers.all()])
        }
        bouquet_list.append(bouquet_data)

    selected_bouquet = random.choice(bouquet_list) if bouquet_list else None
    return render(request, 'result.html', {"bouquet": selected_bouquet})


def order(request, id):
    bouquet = get_object_or_404(Bouquet, id=id)

    if request.method == 'POST':
        name = request.POST.get('fname')
        phone = request.POST.get('tel')
        address = request.POST.get('adres')
        slot_value = request.POST.get('orderTime')

        if not slot_value or '|' not in slot_value:
            messages.error(request, 'Пожалуйста, выберите интервал доставки.')
            return render(
                request,
                'order.html',
                {'bouquet': bouquet, 'time_slots': get_available_slots()}
            )

        try:
            start_str, end_str = slot_value.split('|')
            start_time = time.fromisoformat(start_str)
            end_time = time.fromisoformat(end_str)
        except ValueError:
            messages.error(request, 'Некорректный формат времени доставки.')
            return render(
                request,
                'order.html',
                {'bouquet': bouquet, 'time_slots': get_available_slots()}
            )

        # проверка доступности если уже на странице
        available_slots = get_available_slots()
        chosen_slot = next(
            (s for s in available_slots if s['start'] == start_time and s['end'] == end_time),
            None
        )
        if not chosen_slot:
            messages.error(
                request,
                'Выбранный интервал доставки более недоступен. Пожалуйста, выберите другой.'
            )
            return render(
                request,
                'order.html',
                {'bouquet': bouquet, 'time_slots': available_slots}
            )

        try:
            order = Order.objects.create(
                bouquet=bouquet,
                client_name=name,
                phone_number=phone,
                address=address,
                delivery_time_start=start_time,
                delivery_time_end=end_time,
                payment_status='pending'
            )
        except Exception as e:
            messages.error(request, f'Ошибка при создании заказа:{e}')
            return render(
                request,
                'order.html',
                {'bouquet': bouquet, 'time_slots': get_available_slots()}
            )

        try:
            payment_url = create_payment(order)
            return redirect(payment_url)
        except Exception as e:
            messages.error(request, f'Не удалось создать платёж: {e}')
            return render(
                request,
                'order.html',
                {'bouquet': bouquet, 'time_slots': get_available_slots()}
            )

    available_slots = get_available_slots()
    return render(
        request,
        'order.html',
        {'bouquet': bouquet, 'time_slots': available_slots}
    )


def payment_result(request):
    return render(request, 'payment_result.html')


@csrf_exempt
@require_http_methods(["POST"])
def yookassa_webhook_view(request):
    yookassa_webhook(request.body)
    # Сервису юкасса нужен ответ 200
    return HttpResponse(status=200)
