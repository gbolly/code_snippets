from rest_framework import serializers
from .models import Wallet, Transaction
from apps.shopping.utitlities import get_current_dollar_rate


class WalletSerializer(serializers.ModelSerializer):
    balance_naira = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        exclude = ('created_at', 'deleted_at', 'uuid', 'updated_at')

    def get_balance_naira(self, obj):
        naira_value = obj.balance * get_current_dollar_rate()
        return naira_value


class TransactionSerializer(serializers.ModelSerializer):
    transaction_type = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        exclude = ('deleted_at', 'uuid',
                   'credit_to', 'debit_to', 'updated_at')

    def get_transaction_type(self, obj):
        if obj.credit_to and obj.debit_to:
            return None

        if obj.credit_to or obj.debit_to:
            if obj.credit_to:
                return "credit"
            if obj.debit_to:
                return 'debit'


class GetTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ('deleted_at', 'uuid', 'updated_at')
