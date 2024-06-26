from django.contrib.auth.models import User
from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    is_operating = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        self.is_operating = False
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=100)


class Dish(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, related_name="dishes", on_delete=models.PROTECT)
    restaurant = models.ForeignKey(Restaurant, related_name="dishes", on_delete=models.PROTECT)
    is_available = models.BooleanField(default=True)

    def delete(self, *args, **kwargs):
        self.is_available = False
        self.save()


class Order(models.Model):
    STATUSES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]

    user = models.ForeignKey(User, related_name="orders", on_delete=models.PROTECT)
    restaurant = models.ForeignKey(Restaurant, related_name="orders", on_delete=models.PROTECT)
    dishes = models.ManyToManyField(Dish, through="OrderItem")
    status = models.CharField(max_length=10, choices=STATUSES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.PROTECT)
    dish = models.ForeignKey(Dish, related_name="dishes", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
