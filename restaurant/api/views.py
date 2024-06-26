import logging
from typing import Any, Dict, Optional

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response

from pubsub.publisher import PikaPublisher
from restaurant import models
from restaurant.api.pagination import CustomListOrdersPagination
from restaurant.api.serializers import OrderListSerializer, OrderSerializer

logger = logging.getLogger("restaurant.api.views")


@api_view(["POST"])
@parser_classes([JSONParser])
def create_order(request: Request) -> Response:
    """Creates order with given parameters

    :param request: Request body includes user, restaurant and ordered dishes with their quantities
    :type request: Request
    :return: Created order
    :rtype: Response
    """
    data: Dict[str, Any] = request.data
    user_id = data.get("user")
    restaurant_id = data.get("restaurant")
    dishes_data = data.get("dishes", [])

    if not models.User.objects.filter(pk=user_id).exists():
        return Response({"detail": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST)

    if not models.Restaurant.objects.filter(pk=restaurant_id).exists():
        return Response({"detail": "Invalid restaurant ID"}, status=status.HTTP_400_BAD_REQUEST)

    errors = []
    for dish_data in dishes_data:
        dish_id = dish_data.get("dish")
        quantity = dish_data.get("quantity")

        if not models.Dish.objects.filter(pk=dish_id).exists():
            errors.append(f"Invalid dish ID: {dish_id}")
        elif quantity <= 0:
            errors.append(
                f"Invalid quantity for dish ID {dish_id}: Quantity must be greater than zero"
            )

    if errors:
        return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

    serializer = OrderSerializer(data=data, context={"dishes": data["dishes"]})
    if serializer.is_valid(raise_exception=True):
        order = serializer.save()

        order_id = order.id
        message = {"order_id": order_id}
        PikaPublisher().publish(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def list_orders(request: Request) -> Response:
    """Returns list of all orders. Optionally it can be filtereed by order status.

    :param request: There can be status for filtering orders.
    :type request: Request
    :return: List of orders
    :rtype: Response
    """
    queryset = models.Order.objects.all()
    status_param = request.query_params.get("status")
    if status_param:
        queryset = queryset.filter(status=status_param)

    paginator = CustomListOrdersPagination()
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = OrderListSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
@parser_classes([JSONParser])
def process_order(request: Request) -> Response:
    """Process order with given order_id

    :param request: Request body includes order_id
    :type request: Request
    :return: message
    :rtype: Response
    """
    logger.error(request.data)
    order_id: Optional[int] = request.data.get("order_id")
    order = get_object_or_404(models.Order, id=order_id)

    if order.status == "pending":
        order.status = "completed"
        order.save()
        return Response({"message": "Order completed successfully."}, status=status.HTTP_200_OK)
    elif order.status == "completed":
        logger.warning(f" Order with order_id: {order.pk} is already completed. ")
        return Response({"message": "Order alredy completed."}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"message": "Order cannot be completed."}, status=status.HTTP_400_BAD_REQUEST
        )
