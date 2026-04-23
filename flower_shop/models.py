from django.db import models


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
    name = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True)
    events = models.ManyToManyField(Event, related_name='bouquets')
    flowers = models.ManyToManyField(Flower, related_name='bouquets')
    width = models.CharField(max_length=10)
    height = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='bouquets/')

    def __str__(self):
        return self.name


class Order(models.Model):
    bouquet = models.ForeignKey(
        Bouquet, related_name='orders',
        on_delete=models.CASCADE
    )
    client_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'''Букет {self.bouquet.name}, заказчик {self.client_name},
        телефон {self.phone_number}, адрес {self.address}'''
