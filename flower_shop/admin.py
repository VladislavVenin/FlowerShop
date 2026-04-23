from .models import Flower, Bouquet, Order, Event
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(Bouquet)
class BouquetAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'price', 'image_preview',
        'is_available', 'created_at'
    )
    list_editable = ('price', )
    editable_fields = ('name', 'price')
    search_fields = ('name',)
    filter_horizontal = ('flowers', 'events')

    def image_preview(self, obj):
        html_template = (
            '''<img src="{}" style="max-width: 200px;
            max-height: 200px;" alt="{}" />'''
        )
        return format_html(html_template, obj.image.url, obj.name)


class BouquetNullFilter(SimpleListFilter):
    title = "Ожидает консультации"
    parameter_name = 'bouquet__isnull'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Есть букет'),
            ('no', 'Нет букета'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(bouquet__isnull=False)
        if self.value() == 'no':
            return queryset.filter(bouquet__isnull=True)
        return queryset


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'bouquet', 'client_name', 'phone_number',
        'address', 'payment_status_display',
        'created_at'
    )

    search_fields = ('client_name', 'phone_number', 'address')

    def payment_status_display(self, obj):
        status_map = {
            'pending': 'Ожидает оплаты',
            'paid': 'Оплачено',
            'failed': 'Не оплачено',
        }

        return status_map.get(obj.payment_status, obj.payment_status)

    payment_status_display.short_description = 'Статус платежа'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
