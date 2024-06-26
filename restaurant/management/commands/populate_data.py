from django.core.management.base import BaseCommand

from restaurant.models import Category, Dish, Restaurant, User


class Command(BaseCommand):
    help = "Populate initial data for the application"

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="testuser").exists():
            User.objects.create_user(
                username="testuser", email="testuser@example.com", password="testpassword"
            )

        if not Restaurant.objects.filter(name="Restaurant 1").exists():
            Restaurant.objects.create(
                name="Restaurant 1", address="123 Main St", phone="123-456-7890", is_operating=True
            )

        if not Category.objects.filter(name="Category 1").exists():
            Category.objects.create(name="Category 1")

        if not Dish.objects.filter(name="Dish 1").exists():
            Dish.objects.create(
                name="Dish 1",
                description="Description of Dish 1",
                price=15.99,
                category_id=1,
                restaurant_id=1,
                is_available=True,
            )
