from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Flower(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Цветок'
        verbose_name_plural = 'Цветы'

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'

    def __str__(self):
        return self.name


class Bouquet(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    description = models.TextField(
        null=True,
        verbose_name='Описание'
    )
    events = models.ManyToManyField(
        Event,
        related_name='bouquets',
        verbose_name='События'
    )
    flowers = models.ManyToManyField(
        Flower,
        related_name='bouquets',
        verbose_name='Цветы'
    )
    width = models.CharField(
        max_length=10,
        verbose_name='Ширина'
    )
    height = models.CharField(
        max_length=10,
        verbose_name='Высота'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступен'
    )
    is_recommended = models.BooleanField(
        default=False,
        verbose_name='Рекомендуемый'
    )
    image = models.ImageField(
        upload_to='bouquets/',
        verbose_name='Изображение'
    )

    class Meta:
        ordering = ('-is_recommended',)
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'

    def __str__(self):
        return self.name


class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('failed', 'Не оплачено'),
    ]

    bouquet = models.ForeignKey(
        Bouquet,
        related_name='orders',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        verbose_name='Букет'
    )
    client_name = models.CharField(
        max_length=50,
        verbose_name='Имя клиента'
    )
    phone_number = PhoneNumberField(
        region='RU',
        verbose_name='Номер телефона'
    )
    address = models.CharField(
        max_length=100,
        verbose_name='Адрес доставки'
    )
    delivery_time_start = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Время доставки с'
    )
    delivery_time_end = models.TimeField(
        null=True,
        blank=True,
        verbose_name='Время доставки по'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='Статус платежа'
    )
    yookassa_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID транзакции в ЮKassa'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        if self.bouquet:
            bouquet_name = self.bouquet.name
        else:
            bouquet_name = "ещё не выбран"
        return f'''Букет {bouquet_name}, заказчик {self.client_name},
        телефон {self.phone_number}, адрес {self.address}'''
