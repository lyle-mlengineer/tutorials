class ApplicationError(Exception):
    """Base exception for all application errors"""


class AuthenticationError(ApplicationError):
    """Base exception for all authentication errors"""


class AccountNotFoundError(AuthenticationError):
    """Raised when an account is not found"""


class AccountAlreadyExistsError(AuthenticationError):
    """Raised when an account already exists"""


class InvalidCredentialsError(AuthenticationError):
    """Raised when invalid credentials are provided"""


class AccountNotActiveError(AuthenticationError):
    """Raised when an account is not active"""


class UserLoggedOutError(AuthenticationError):
    """Raised when a user is logged out"""


class AuthorizationError(ApplicationError):
    """Base exception for all authorization errors"""


class UnauthorizedError(AuthorizationError):
    """Raised when a user is not authorized to perform an action"""


class EventPublicationError(Exception):
    """Raised when an error occurs when publishing events."""


class DatabaseChangesPublishingError(Exception):
    """Raised when an error occurs when publishing database changes."""
