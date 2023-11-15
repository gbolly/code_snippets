from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from betaeshopping.utilities import make_params


from .serializers import WalletSerializer, TransactionSerializer, GetTransactionSerializer
from .models import Wallet, Transaction, TransactionStatus
from apps.shopping.models import Order
from .utils import process_payment
import logging

db_logger = logging.getLogger("db")


class TransactionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    type = make_params(title='type', description="type", type="STRING")
    reference = make_params(
        title='reference', description="reference", type="STRING")

    @swagger_auto_schema(manual_parameters=[type, reference])
    def get(self, request):
        _type = request.query_params.get("type")
        reference = request.query_params.get("reference")
        user = request.user
        wallet = user.wallet
        filter = {}

        transactions_filtered = False
        transactions = Transaction.active_objects.order_by("-created_at")
        if reference:
            filter["reference"] = reference
            transactions_filtered = True

        if _type == "wallet":
            transactions = transactions.filter(
                Q(debit_to=wallet) | Q(credit_to=wallet))
            transactions_filtered = True

        if _type == "order":
            orders = Order.objects.filter(
                transaction__isnull=False, shopper=user)
            transaction_ids = orders.values_list('transaction_id', flat=True)
            filter["id__in"] = transaction_ids
            transactions_filtered = True

        if not transactions_filtered:
            orders = Order.objects.filter(
                transaction__isnull=False, shopper=user)
            transaction_ids = orders.values_list('transaction_id', flat=True)
            transactions = transactions.filter(
                Q(id__in=transaction_ids) | Q(
                    debit_to=wallet) | Q(credit_to=wallet)
            ).order_by('-created_at')
        transactions = transactions.filter(**filter)

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WalletAPIView(APIView):
    permission_classes = [IsAuthenticated]

    """
    Get authenticated user's wallet
    """

    def get(self, request):
        # Retrieve the user's wallet object
        wallet = Wallet.objects.get(user=request.user)
        serializer = WalletSerializer(wallet, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    transaction_id = make_params(
        title='transaction_id', description="Verify/Create Wallet Transaction", type="NUM")
    dollar_value = make_params(
        title='dollar_value', description="Dollar Value", type="NUM")

    @swagger_auto_schema(manual_parameters=[transaction_id, dollar_value])
    def post(self, request):
        req_data = request.data
        wallet = request.user.wallet
        dollar_value = req_data['dollar_value']

        # Wrap the payment processing in a transaction
        try:
            with transaction.atomic():
                transaction_data = process_payment(req_data, wallet)

                serializer = GetTransactionSerializer(data=transaction_data)
                if not serializer.is_valid():
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    serializer.save()

                if serializer.instance.status == TransactionStatus.SUCCESSFUL:
                    wallet.deposit(dollar_value)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    if serializer.instance.status == TransactionStatus.FAILED:
                        message = serializer.instance.reason_for_failure
                        db_logger.warning(
                            f'error depositing to {wallet.user.email} wallet - {message}')
                    return Response(serializer.data, status=status.HTTP_502_BAD_GATEWAY)

        except Exception as e:
            db_logger.exception(e)
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
