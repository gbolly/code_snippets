from django.contrib import admin, messages
from apps.payments.models import Wallet, Transaction, TransactionStatus
from .forms import TransactionForm


class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance',)
    readonly_fields = ('user', 'balance', 'deleted_at',)
    search_fields = ('user__email',)


class TransactionAdmin(admin.ModelAdmin):
    form = TransactionForm
    list_display = ('reference', 'value', 'status',
                    'credit_to', 'debit_to', "created_at")
    list_filter = ('status', 'credit_to', 'debit_to')
    search_fields = ('reference', 'payment_provider_txn_id',)
    readonly_fields = ('deleted_at', 'updated_by',)

    def save_model(self, request, obj, form, change):
        # Call the clean method to trigger validation and apply logic
        if form.is_valid():
            form.instance.updated_by = request.user
            try:
                reference, value, message = form.process_transaction()
            except Exception as e:
                self.message_user(request, str(e), level=messages.ERROR)
                return

            form.instance.reference = reference
            form.instance.value = value

            if message:
                messages.success(request, message)
            return super().save_model(request, obj, form, change)

    def message_user(self, request, message, level=messages.SUCCESS, extra_tags='', fail_silently=False):
        if level == messages.ERROR:
            super().message_user(request, message, level, extra_tags, fail_silently)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == TransactionStatus.SUCCESSFUL:
            return self.readonly_fields + tuple(
                [
                    item.name
                    for item in obj._meta.fields
                    if item.name not in ["deleted_at", "updated_by", ]
                ]
            )
        else:
            return self.readonly_fields


admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction, TransactionAdmin)
