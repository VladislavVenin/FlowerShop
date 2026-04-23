from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Flower(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Bouquet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True)
    events = models.ManyToManyField(Event, related_name='bouquets')
    flowers = models.ManyToManyField(Flower, related_name='bouquets')
    width = models.CharField(max_length=10)
    height = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    is_recommended = models.BooleanField(default=False)
    image = models.ImageField(upload_to='bouquets/')

    class Meta:
        ordering = ('-is_recommended',)
        verbose_name = 'Букет'
        verbose_name_plural = 'Букеты'

    def __str__(self):
        return self.name


class Order(models.Model):
    bouquet = models.ForeignKey(
        Bouquet, related_name='orders',
        blank=True, null=True,
        on_delete=models.CASCADE
    )
    client_name = models.CharField(max_length=50)
    phone_number = PhoneNumberField(region='RU')
    address = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.bouquet:
            bouquet_name = self.bouquet.name
        else:
            bouquet_name = "ещё не выбран"
        return f'''Букет {bouquet_name}, заказчик {self.client_name},
        телефон {self.phone_number}, адрес {self.address}'''
