from apps.payments.models import TransactionStatus
from apps.shopping.services import FlutterWaveServices
from datetime import datetime
from .serializers import TransactionSerializer


def update_transaction_reference(credit_to, debit_to, reference):
    if reference.startswith('BESW') or reference.startswith('BES'):
        return reference

    if credit_to or debit_to:
        return "BESW-" + reference
    return "BES-" + reference


def process_successful_transaction(credit_to, debit_to, value):

    if credit_to and not credit_to.deleted_at:
        # Credit the wallet associated with the Transaction
        credit_to.deposit(value)
        message = (f'''The transaction was successfully updated, and ${value} 
        has been added to {credit_to.user.email} wallet.''')

    if debit_to and not debit_to.deleted_at:
        # Debit the wallet associated with the Transaction
        debit_to.withdraw(value)
        message = (
            f'''The transaction was successfully updated, and ${value} 
            has been removed from {debit_to.user.email} wallet.'''
        )

    return message


def map_payment_status(payment_status):
    status_mapping = {
        "successful": TransactionStatus.SUCCESSFUL,
        "failure": TransactionStatus.FAILED,
        "pending": TransactionStatus.PENDING,
    }
    return status_mapping.get(payment_status, TransactionStatus.PENDING)


def generate_transaction_reference(prefix):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d%H%M%S")
    tx_ref = f"{prefix}-{formatted_datetime}"
    return tx_ref


def process_payment(req_data, wallet=None, order=None):
    # Verify payment transaction using FlutterWaveServices
    payment_verify = FlutterWaveServices.verify_transaction(
        transaction_id=req_data.get("transaction_id")
    )
    # Extract data from the verification response
    data = payment_verify.get("data")

    transaction_amount = req_data.get('dollar_value', data.get("amount"))

    # Construct transaction data dictionary
    transaction_data = {
        "reference": data.get("tx_ref"),
        "payment_provider_txn_id": data.get("id"),
        "value": transaction_amount,
        "status": map_payment_status(data.get("status")),
        "payment_type": f'{data.get("payment_type")}({data.get("currency")})'
    }

    if data.get("status") == "failure":
        transaction_data["reason_for_failure"] = data.get("message")

    if wallet:
        transaction_data["credit_to"] = wallet.id
        transaction_data["description"] = transaction_description(
            None, transaction_amount)
    else:
        transaction_data["currency"] = data.get("currency")
        transaction_data["description"] = transaction_description(order)

    # Return processed transaction data
    return transaction_data


def create_or_update_transaction(data, instance=None):
    if instance:
        serializer = TransactionSerializer(instance, data=data, partial=True)
    else:
        serializer = TransactionSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer


def transaction_description(order_obj=None, amount=None):
    if order_obj:
        return f'Payment for order #{order_obj.order_id}'
    elif amount:
        return f'Funded wallet with {amount}'
