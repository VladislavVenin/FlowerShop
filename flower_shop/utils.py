from datetime import datetime, timedelta

from django.utils import timezone


def get_available_slots() -> list[dict]:
    '''Создает список доступных слотов для заказа'''

    now = timezone.localtime(timezone.now())
    current_time = now.time()

    start_hour = 10
    end_hour = 20
    slot_duration_hours = 2
    prep_minutes = 60

    slots = []
    slot_start = datetime(now.year, now.month, now.day, start_hour, 0, tzinfo=now.tzinfo)
    end_limit = datetime(now.year, now.month, now.day, end_hour, 0, tzinfo=now.tzinfo)

    while slot_start < end_limit:
        slot_end = slot_start + timedelta(hours=slot_duration_hours)
        start_time = slot_start.time()
        end_time = slot_end.time()

        # пропуск если слот закончился
        if end_time <= current_time:
            slot_start = slot_end
            continue

        # пропуск если до минимального времени из слота меньше 60 минут
        minutes_to_start = (slot_start - now).total_seconds() / 60
        if minutes_to_start < prep_minutes:
            slot_start = slot_end
            continue

        slots.append({
            'start': start_time,
            'end': end_time,
            'label': f"с {start_time.strftime('%H:%M')} до {end_time.strftime('%H:%M')}"
        })
        slot_start = slot_end

    return slots
