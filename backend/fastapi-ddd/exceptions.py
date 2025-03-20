# exceptions.py

class DomainError(Exception):
    """Base exception for all domain errors"""

class OrderError(DomainError):
    """Base exception for order-related errors"""

class OrderCreationError(OrderError):
    """Raised when an order cannot be created due to a database constraint"""

class ProductNotFoundError(OrderError):
    """Raised when a referenced product doesn't exist"""

class DuplicateOrderItemError(OrderError):
    """Raised when trying to add the same product twice to an order"""

class InvalidOrderDataError(OrderError):
    """Raised when order data violates domain rules"""

class InsufficientItemsError(OrderError):
    """Raised when trying to order more items than available in inventory"""

class InventoryError(DomainError):
    """Base exception for inventory-related errors"""

class CustomerError(DomainError):
    """Base exception for customer-related errors"""