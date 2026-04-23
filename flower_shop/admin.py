from .models import Flower, Bouquet, Order, Event
from django.contrib import admin
from django.utils.html import format_html


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'bouquet', 'client_name', 'phone_number',
        'address', 'created_at'
    )
    search_fields = ('client_name', 'phone_number', 'address')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
