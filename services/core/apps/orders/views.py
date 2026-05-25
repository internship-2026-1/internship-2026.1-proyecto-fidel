"""vistas para ordenes"""
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from apps.utils import build_response
from .models import Order
from .serializers import OrderSerializers
from rest_framework.response import Response
from .services import OrderService
import traceback

class OrderCreateListViews(APIView):
    """listar y crear ordenes"""

    def get(self, request):
        """listar los ordenes"""
        orders = Order.objects.all().order_by("-created_at")
        serializer = OrderSerializers(orders, many=True)

        payload = build_response(
            success=True,
            message="Órdenes listadas correctamente",
            body=serializer.data,
            status_code=status.HTTP_200_OK,
        )
        return Response(payload, status=status.HTTP_200_OK)

    def post(self, request):
        """crear ordenes"""
        serializer = OrderSerializers(data=request.data)

        if not serializer.is_valid():
            payload = build_response(
                success=False,
                message="satos inválidos",
                body=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = OrderService.create_order_with_stock_check(
                customer_id=serializer.validated_data["customer_id"],
                customer_name=serializer.validated_data.get("customer_name"),
                items_data=serializer.validated_data["items"],
            )

            response_serializer = OrderSerializers(order)

            payload = build_response(
                success=True,
                message="orden creada correctamente",
                body=response_serializer.data,
                status_code=status.HTTP_201_CREATED,
            )
            return Response(payload, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(traceback.format_exc())
            payload = build_response(
                success=False,
                message="Error al crear la orden",
                body={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailViews(APIView):
    """Ver detalle de una orden."""

    def get(self, request, pk):
        """obtener detalles de una orden"""
        order = Order.objects.filter(id=pk).first()

        if not order:
            payload = build_response(
                success=False,
                message="Orden no encontrada",
                body={"id": pk},
                status_code=status.HTTP_404_NOT_FOUND,
            )
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializers(order)

        payload = build_response(
            success=True,
            message="Orden encontrada",
            body=serializer.data,
            status_code=status.HTTP_200_OK,
        )
        return Response(payload, status=status.HTTP_200_OK)

class SimulandoPago(APIView):
    """simular pago exitoso de una orden descuenta stock y manda sincronizar odoo"""

    def post(self, request, pk):
        try:
            order = OrderService.simulate_payment(order_id=pk)
            serializer = OrderSerializers(order)

            payload = build_response(
                success=True,
                message="Pago simulado correctamente",
                body=serializer.data,
                status_code=status.HTTP_200_OK,
            )
            return Response(payload, status=status.HTTP_200_OK)

        except Exception as e:
            payload = build_response(
                success=False,
                message="Error al simular pago",
                body={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)


class OrderByCustomerViews(APIView):
    """listar orders por customer_id"""

    def get(self, request, customer_id):
        orders = Order.objects.filter(customer_id=customer_id).order_by("-created_at")
        serializer = OrderSerializers(orders, many=True)

        payload = build_response(
            success=True,
            message="ordenes del cliente listadas correctamente",
            body=serializer.data,
            status_code=status.HTTP_200_OK,
        )

        return Response(payload, status=status.HTTP_200_OK)