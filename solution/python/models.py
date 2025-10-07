from dataclasses import dataclass

@dataclass
class Order:
    order_id: str
    customer_id: str
    category: str
    unit_price: float
    quantity: int
    timestamp: str

    def total(self) -> float:
        return round(self.unit_price * self.quantity, 2)