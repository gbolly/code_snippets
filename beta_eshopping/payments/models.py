from django.db import models
from django.conf import settings
from betaeshopping.soft_deletion_model import SoftDeletionModel
from django.db.models import TextChoices
from .exceptions import InsufficientFunds


class Wallet(SoftDeletionModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="wallet", on_delete=models.CASCADE)
    balance = models.DecimalField(verbose_name="Balance", max_digits=10,
                                  decimal_places=2, blank=True, null=True,
                                  default=0.00)

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if amount > self.balance:
            raise InsufficientFunds()
        self.balance -= amount
        self.save()

    def __str__(self):
        return f"{self.user.email}'s Wallet"


class TransactionStatus(TextChoices):
    PENDING = 'pending', 'Pending'
    SUCCESSFUL = 'successful', 'Successful'
    FAILED = 'failed', 'Failed'


class Transaction(SoftDeletionModel):
    value = models.DecimalField(verbose_name="Transaction Value",
                                max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(verbose_name="Status", max_length=100,
                              choices=TransactionStatus.choices)
    reference = models.CharField(
        verbose_name="Reference Number", unique=True, max_length=100, blank=True, null=True)
    credit_to = models.ForeignKey(Wallet, blank=True, null=True, verbose_name="Credited Wallet",
                                  related_name="credit", on_delete=models.SET(None))
    debit_to = models.ForeignKey(Wallet, blank=True, null=True, verbose_name="Debited Wallet",
                                 related_name="debit", on_delete=models.SET(None))
    reason_for_failure = models.CharField(
        verbose_name="Reason for Failure", max_length=250, blank=True, null=True)
    currency = models.CharField(
        "Currency", max_length=50, blank=True, null=True, default="USD")
    payment_provider_txn_id = models.CharField("Transaction ID",
                                               unique=True, max_length=100, blank=True, null=True
                                               )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True
    )
    payment_type = models.CharField(
        "Payment Type", max_length=100, blank=True, null=True)

    description = models.CharField("Description", max_length=100)

    def __str__(self):
        return self.reference
