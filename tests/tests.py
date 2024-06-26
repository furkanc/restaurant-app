from typing import Dict, List
from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITransactionTestCase

from restaurant.api.pagination import CustomListOrdersPagination
from restaurant.api.serializers import OrderListSerializer
from restaurant.models import Category, Dish, Order, OrderItem, Restaurant


class BaseTestCase(APITransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.restaurant = Restaurant.objects.create(
            name="Test Restaurant", address="123 Test St", phone="1234567890"
        )
        self.category = Category.objects.create(name="Test Category")
        self.dish = Dish.objects.create(
            name="Test Dish",
            description="Test Description",
            price=10.00,
            category=self.category,
            restaurant=self.restaurant,
        )
        self.dish_2 = Dish.objects.create(
            name="Test Dish 2",
            description="Test Description 2",
            price=20.00,
            category=self.category,
            restaurant=self.restaurant,
        )

    def create_data(
        self, user_id: int, restaurant_id: int, dish_id: int, quantity: int
    ) -> Dict[str, int | List[Dict[str, int]]]:
        return {
            "user": user_id,
            "restaurant": restaurant_id,
            "dishes": [{"dish": dish_id, "quantity": quantity}],
        }


class OrderListTests(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.order = Order.objects.create(user=self.user, restaurant=self.restaurant)
        self.order_item = OrderItem.objects.create(order=self.order, dish=self.dish, quantity=2)

    def test_order_list(self):
        url = reverse("list_orders")
        factory = APIRequestFactory()
        request = factory.get(url)

        request.query_params = request.GET

        response = self.client.get(url, request=request)
        orders = Order.objects.all()
        paginator = CustomListOrdersPagination()
        paginated_orders = paginator.paginate_queryset(orders, request)
        serializer = OrderListSerializer(paginated_orders, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, paginator.get_paginated_response(serializer.data).data)


class CreateOrderTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    @patch("restaurant.api.views.PikaPublisher.publish")
    def test_create_order(self, mock_publish):
        mock_publish.return_value = None

        url = reverse("create_order")
        data = self.create_data(self.user.id, self.restaurant.id, self.dish.id, 1)

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Order.objects.filter(user=self.user, restaurant=self.restaurant).exists())
        order = Order.objects.get(user=self.user, restaurant=self.restaurant)
        mock_publish.assert_called_once_with({"order_id": order.id})

    @patch("restaurant.api.views.PikaPublisher.publish")
    def test_create_order_with_multiple_dish(self, mock_publish):
        mock_publish.return_value = None

        url = reverse("create_order")
        data = self.create_data(self.user.id, self.restaurant.id, self.dish.id, 1)

        data["dishes"].append({"dish": self.dish_2.id, "quantity": 2})

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch("restaurant.api.views.PikaPublisher.publish")
    def test_create_order_non_existent_dish(self, mock_publish):
        """
        Returns 400 because of non-existent dish
        """
        mock_publish.return_value = None

        url = reverse("create_order")
        data = self.create_data(self.user.id, self.restaurant.id, 15, 1)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Order.objects.filter(user=self.user, restaurant=self.restaurant).exists())

    @patch("restaurant.api.views.PikaPublisher.publish")
    def test_create_order_negative_quantity(self, mock_publish):
        """
        Returns 400 because of negative quantity
        """
        mock_publish.return_value = None

        url = reverse("create_order")
        data = self.create_data(self.user.id, self.restaurant.id, self.dish.id, -1)

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(Order.objects.filter(user=self.user, restaurant=self.restaurant).exists())
