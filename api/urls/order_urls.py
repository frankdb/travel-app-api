from django.urls import path

from api.views.order_views import CreateCheckoutSession, OrderList, StripeWebhook

urlpatterns = [
    path("create-checkout-session/", CreateCheckoutSession.as_view()),
    path("orders/", OrderList.as_view()),
    path("webhook/", StripeWebhook.as_view()),
]
