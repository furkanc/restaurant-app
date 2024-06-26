from typing import Any, Dict

from rest_framework import serializers

from restaurant.models import Dish, Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    dish = serializers.PrimaryKeyRelatedField(queryset=Dish.objects.all())
    quantity = serializers.IntegerField()

    class Meta:
        model = OrderItem
        fields = ["dish", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    dishes = serializers.SerializerMethodField()
    status = serializers.CharField(default="pending", required=False)

    class Meta:
        model = Order
        fields = ["user", "restaurant", "dishes", "status"]

    def create(self, validated_data: Dict[str, Any]):
        dishes_data = self.context.get("dishes")
        if dishes_data is None:
            raise serializers.ValidationError("dishes data is required")

        order = Order.objects.create(**validated_data)
        for dish_data in dishes_data:
            dish_instance = Dish.objects.get(id=dish_data["dish"])
            OrderItem.objects.create(
                order=order, dish=dish_instance, quantity=dish_data["quantity"]
            )

        return order

    def get_dishes(self, instance):
        qs = instance.order_items.all()
        serialzer = OrderItemSerializer(qs, many=True)
        return serialzer.data


class OrderListSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()
    restaurant = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ["id", "user", "restaurant", "status", "created_at", "updated_at", "order_items"]
