from typing import List

from django.urls import URLPattern, path

from restaurant.api import views

urlpatterns: List[URLPattern] = [
    path("create_order/", views.create_order, name="create_order"),
    path("process_order/", views.process_order, name="process_order"),
    path("list_orders/", views.list_orders, name="list_orders"),
]
