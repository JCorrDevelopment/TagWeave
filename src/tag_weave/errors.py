class TagWeaveError(Exception):
    """Base class for exceptions in this module."""


class TagIsInvalidError(TagWeaveError):
    """Raised when the tag specification is invalid."""


class TemplateValidationError(TagWeaveError):
    """Raised when the template string is invalid."""


class TagMappingAlreadyExistsError(TagWeaveError):
    """Raised when the encoder is already set."""


class InvalidTagSpecError(TagWeaveError):
    """Raised when the tag cannot be created from the given specification."""


class DecoderIsNotProvidedError(TagWeaveError):
    """Raised when the decoder is not provided for the tag."""
