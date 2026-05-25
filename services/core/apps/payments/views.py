"""views para payments """
import os
import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.utils import build_response
from apps.orders.models import Order
from .models import Payment
from .serializers import CreateCheckoutSessionSerializer
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BaseAuthentication
from apps.orders.models import Order
from apps.orders.services import OrderService

# Create your views here.
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class CreateCheckoutSessionView(APIView):
    """crear sesion de pago stripe checkout"""

    def post(self, request):
        serializer = CreateCheckoutSessionSerializer(data=request.data)

        if not serializer.is_valid():
            payload = build_response(
                success=False,
                message="datos invalidos",
                body=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload, status=status.HTTP_400_BAD_REQUEST)

        order_id = serializer.validated_data["order_id"]
        order = Order.objects.filter(id=order_id).first()

        if not order:
            payload = build_response(
                success=False,
                message="orden no encontrada",
                body={"order_id": order_id},
                status_code=status.HTTP_404_NOT_FOUND,
            )
            return Response(payload, status=status.HTTP_404_NOT_FOUND)

        try:
            amount_cents = int(float(order.total_amount) * 100)

            session = stripe.checkout.Session.create(
                mode="payment",
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "gtq",
                            "product_data": {
                                "name": f"Orden {order.id}",
                            },
                            "unit_amount": amount_cents,
                        },
                        "quantity": 1,
                    }
                ],
                metadata={
                    "order_id": str(order.id),
                },
                payment_intent_data={
                    "metadata": {
                        "order_id": str(order.id),
                    }
                },
                success_url=os.getenv("STRIPE_SUCCESS_URL"),
                cancel_url=os.getenv("STRIPE_CANCEL_URL"),
            )

            payment = Payment.objects.create(
                order_id=str(order.id),
                stripe_session_id=session.id,
                stripe_checkout_url=session.url,
                amount=order.total_amount,
                currency="gtq",
                status="pending",
            )

            payload = build_response(
                success=True,
                message="checkout session creada correctamente",
                body={
                    "payment_id": str(payment.id),
                    "order_id": str(order.id),
                    "checkout_url": session.url,
                    "stripe_session_id": session.id,
                },
                status_code=status.HTTP_200_OK,
            )
            return Response(payload, status=status.HTTP_200_OK)

        except Exception as e:
            payload = build_response(
                success=False,
                message="error al crear checkout session",
                body={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
            return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """recibe eventos de stripe y confirma pagos"""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                webhook_secret
            )
        except ValueError:
            payload_response = build_response(
                success=False,
                message="payload invalido",
                body={},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload_response, status=status.HTTP_400_BAD_REQUEST)

        except stripe.error.SignatureVerificationError:
            payload_response = build_response(
                success=False,
                message="firma stripe invalida",
                body={},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(payload_response, status=status.HTTP_400_BAD_REQUEST)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]

            stripe_session_id = session["id"]
            order_id = session["metadata"]["order_id"]
    
            print("WEBHOOK CHECKOUT COMPLETED")
            print("STRIPE SESSION:", stripe_session_id)
            print("ORDER ID:", order_id)
       
            payment = Payment.objects.filter(
                stripe_session_id=stripe_session_id
            ).first()
       
            if payment:
                payment.status = "paid"
                payment.stripe_event_id = event["id"]
                payment.paid_at = timezone.now()
                payment.save()
      
            order = Order.objects.filter(id=order_id).first()
     
            print("ORDER FOUND:", order, flush=True)
     
            if order and order.status == Order.STATUS_PENDING:
                OrderService.simulate_payment(order_id=order.id)
    
        if event["type"] == "payment_intent.payment_failed":
            payment_intent = event["data"]["object"]
            order_id = payment_intent["metadata"]["order_id"]
        
            order = Order.objects.filter(id=order_id).first()
      
            if order:
                order.status = Order.STATUS_FAILED
                order.save(update_fields=["status", "updated_at"])


        payload_response = build_response(
            success=True,
            message="webhook recibido correctamente",
            body={"event_type": event["type"]},
            status_code=status.HTTP_200_OK,
        )

        return Response(payload_response, status=status.HTTP_200_OK)