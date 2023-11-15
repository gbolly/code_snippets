

class InsufficientFunds(Exception):
    errMsg = "Insufficient funds. Please add funds to your wallet to complete\
            the payment or choose an alternative payment method."
    
    def __init__(self, message=errMsg):
        self.message = message
        super().__init__(self.message)
