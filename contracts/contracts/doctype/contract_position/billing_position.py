from .billing_period import BillingPeriod
from .contract_position import ContractPosition

class BillingPosition:
    """Represents a billing position of a contract position.
    """
    def __init__(self, contract_position: ContractPosition, billing_period: BillingPeriod):
        self.contract_position = contract_position
        self.billing_period = billing_period