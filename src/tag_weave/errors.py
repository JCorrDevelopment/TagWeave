class TagWeaveError(Exception):
    """Base class for exceptions in this module."""


class TagIsInvalidError(TagWeaveError):
    """Raised when the tag specification is invalid."""


class TemplateValidationError(TagWeaveError):
    """Raised when the template string is invalid."""


class EncoderAlreadySetError(TagWeaveError):
    """Raised when the encoder is already set."""
