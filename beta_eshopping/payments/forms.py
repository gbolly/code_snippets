from django import forms
from .models import Transaction, TransactionStatus
from .utils import (
    update_transaction_reference,
    process_successful_transaction,
)


class TransactionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Transaction
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        credit_to = cleaned_data.get("credit_to")
        value = cleaned_data.get("value")
        debit_to = cleaned_data.get("debit_to")
        reference = cleaned_data.get("reference")

        if not value:
            self.add_error(
                'value', "Value is required!")

        if not reference:
            self.add_error(
                'reference', "Reference is required!")

        if credit_to and debit_to:
            self.add_error(
                'credit_to', "Credited and Debited Wallet cannot be provided at the same time!")
            self.add_error(
                'debit_to', "Credited and Debited Wallet cannot be provided at the same time!")

        if debit_to:
            if value > debit_to.balance:
                self.add_error(
                    'value', f"Insufficient funds. {debit_to.user.first_name} balance is {debit_to.balance} USD")

    def process_transaction(self):
        status = self.cleaned_data.get("status")
        credit_to = self.cleaned_data.get("credit_to")
        reference = self.cleaned_data.get("reference")
        debit_to = self.cleaned_data.get("debit_to")
        value = self.cleaned_data.get("value")
        message = None

        if status == TransactionStatus.SUCCESSFUL:
            reference = update_transaction_reference(
                credit_to, debit_to, reference)
            if credit_to or debit_to:
                message = process_successful_transaction(
                    credit_to, debit_to, value
                )
        return reference, value, message,
