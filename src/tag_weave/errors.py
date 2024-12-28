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


class CodecIsNotProvidedError(TagWeaveError):
    """Raised when the codec is not provided for the tag."""


class ConfigurationError(TagWeaveError):
    """Raised when the configuration is invalid."""


class IncorrectValidatorError(TagWeaveError):
    """Raised when the validator is not valid."""


class IncorrectEncoderError(TagWeaveError):
    """Raised when the encoder is not valid."""
