from django.urls import path

# from rest_framework.urlpatterns import format_suffix_patterns
from apps.payments import views

app_name = 'payments'

urlpatterns = [
    path('wallet/', views.WalletAPIView.as_view(), name='user-wallet'),
    path('transactions/', views.TransactionListAPIView.as_view(), name='user-transactions'),
]
