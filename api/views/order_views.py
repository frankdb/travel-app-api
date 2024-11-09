import stripe
from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models.job_board import Job
from api.models.order import Order
from api.serializers.order_serializers import OrderSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreateCheckoutSession(APIView):
    def post(self, request):
        try:
            price_id = request.data.get("priceId")
            user_id = request.data.get("userId")
            job_id = request.data.get("jobId")

            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{settings.FRONTEND_URL}/payment/canceled",
                metadata={
                    "user_id": user_id,
                    "job_id": job_id,
                },
            )

            return Response({"url": checkout_session.url})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrderList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhook(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )

            if event.type == "checkout.session.completed":
                session = event.data.object

                # Retrieve session with line items
                session_with_items = stripe.checkout.Session.retrieve(
                    session.id, expand=["line_items"]
                )

                # Create order
                Order.objects.create(
                    user_id=session.metadata.get("user_id"),
                    email=session.customer_email,
                    stripe_session_id=session.id,
                    payment_status=Order.Status.PAID,
                    amount_total=session.amount_total / 100,
                    items=session_with_items.line_items.data,
                )

                # Update job status to ACTIVE
                job_id = session.metadata.get("job_id")
                if job_id:
                    try:
                        job = Job.objects.get(id=job_id)
                        job.status = Job.Status.ACTIVE
                        job.save()
                    except Job.DoesNotExist:
                        pass

            return HttpResponse(status=200)

        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)
        except Exception as e:
            return HttpResponse(content=str(e), status=500)
