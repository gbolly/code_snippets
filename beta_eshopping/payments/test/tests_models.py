from model_bakery import baker
from django.test import TestCase
from apps.payments.models import Wallet, Transaction, TransactionStatus
from django.conf import settings
from django.db.models import signals


class WalletModelTest(TestCase):

    def setUp(self):
        signals.post_save.receivers = []
        self.user = baker.make(settings.AUTH_USER_MODEL,
                               email="testuser@example.com")
        self.wallet = Wallet.objects.create(user=self.user)

    def test_wallet_str_representation(self):
        expected_str = "testuser@example.com's Wallet"
        self.assertEqual(str(self.wallet), expected_str)

    def test_auto_timestamps(self):

        # Update the wallet and check if updated_at is greater than created_at
        self.wallet.balance = 200.75
        self.wallet.save()
        self.assertTrue(self.wallet.updated_at > self.wallet.created_at)

    def test_soft_deletion(self):
        # Soft delete the wallet
        self.wallet.delete()
        self.assertIsNotNone(self.wallet.deleted_at)


class TransactionModelTest(TestCase):
    def setUp(self):
        signals.post_save.receivers = []
        self.user = baker.make(settings.AUTH_USER_MODEL, username="test_user")
        self.wallet = Wallet.objects.create(user=self.user)

    def test_transaction_str_representation_pending(self):
        transaction = Transaction.objects.create(
            value=100.50,
            status=TransactionStatus.PENDING,
            reference="ABC123",
            credit_to=self.wallet,
            debit_to=None
        )
        expected_str = "ABC123"
        self.assertEqual(str(transaction), expected_str)
