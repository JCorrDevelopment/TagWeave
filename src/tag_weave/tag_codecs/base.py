from __future__ import annotations

import abc
import dataclasses
import inspect
from collections.abc import Callable
from functools import lru_cache
from importlib import import_module
from typing import Any, TypeIs, cast

from twilight_utils.more_typing.signatures import has_same_signature

from tag_weave.errors import ConfigurationError, DecoderIsNotProvidedError
from tag_weave.tag import Tag

type IDecoder = BaseDecoder | Callable[[str, Tag], str]
"""
Type alias for an decoder object.

Used to simplify type hints and improve readability. Shows that the object should be either a class-based decoder
or a function with the signature `Callable[[str, Tag], str]`.

Decoders are supposed only to transform the content from an encoded format to target, but not to validate it.
Validation should be done before decoding the content or be assumed to be valid beforehand.
"""
type IEncoder = BaseEncoder | Callable[[str, Tag], str]
"""
Type alias for an encoder object.

Used to simplify type hints and improve readability. Shows that the object should be either a class-based encoder
or a function with the signature `Callable[[str, Tag], str]`.

Encoders are supposed only to transform the content from an original template string to a target format, but not to
validate it. Before encoding the content, collection of tag validators should be applied to ensure that the content
is, in face, a valid template string according to registry rules.
"""
type IValidator = BaseValidator | Callable[[str, Tag], None]
"""
Type alias for a validator object.

Used to simplify type hints and improve readability. Shows that the object should be either a class-based validator
or a function with the signature `Callable[[str, Tag], None]`.
"""


class _ByImportStrMixin[T]:
    """Add the ability to create an instance of the object by importing it from a string."""

    @classmethod
    def by_import_str(cls, import_str: str, *args: Any, **kwargs: Any) -> T:  # noqa: ANN401
        """
        Create an instance of the object by importing it from a string.

        Args:
            import_str (str): The string to import the object from.
            *args (Any): Additional positional arguments to pass to the object constructor.
            **kwargs (Any): Additional keyword arguments to pass to the object constructor.

        Returns:
            Self: The new instance of the object.

        Raises:
            ConfigurationError: If the object is not a class or a function.
        """
        module_name, obj_name = import_str.rsplit(".", 1)
        module = import_module(module_name)
        obj = getattr(module, obj_name)
        if inspect.isclass(obj):
            return cast("T", obj(*args, **kwargs))
        if inspect.isfunction(obj):
            return cast("T", obj)
        msg = f"Object {obj_name} is not a class or a function."
        raise ConfigurationError(msg)


class _BaseTransformer[T](_ByImportStrMixin[T], abc.ABC):
    """Base class that specified the interface for an object transformation, such as template encoders and decoders."""

    @abc.abstractmethod
    def __call__(self, content: str, tag: Tag) -> str:
        """
        Transform the string by rules specified in the tag object and provided format_ parameter.

        Args:
            content (str): string or a substring to transform
            tag (Tag): tag object that contains the transformation rules

        Returns:
            str: transformed content
        """


class BaseEncoder(_BaseTransformer[IEncoder], abc.ABC):
    """Base class for a class-based encoders."""

    # noinspection PyTypeHints
    @classmethod
    @lru_cache
    def is_encoder(cls, encoder: Any) -> TypeIs[IEncoder]:  # noqa: ANN401
        """Check if the given encoder matches the expected signature of IEncoder.__call__.

        Args:
            encoder (Callable): The encoder function or callable object to check.

        Returns:
            bool: True if the encoder matches the expected signature, False otherwise.
        """
        if isinstance(encoder, cls):
            return True

        return has_same_signature(encoder, cls.__call__)


class BaseDecoder(_BaseTransformer[IDecoder], abc.ABC):
    """Base class for a class-based decoders."""

    # noinspection PyTypeHints
    @classmethod
    @lru_cache
    def is_decoder(cls, decoder: Any) -> TypeIs[IDecoder]:  # noqa: ANN401
        """Check if the given decoder object matches the expected signature of IDecoder.__call__.

        Args:
            decoder (Any): The decoder function or callable object to check.

        Returns:
            bool: True if the decoder matches the expected signature, False otherwise.
        """
        if isinstance(decoder, cls):
            return True

        return has_same_signature(decoder, cls.__call__)


class BaseValidator(_ByImportStrMixin[IValidator], abc.ABC):
    """
    Specify the interface for a class-based validator.

    A validator is a callable class that used to validate the template string before encoding according to tag
    validation rules.

    The validator should raise an TemplateValidationError if the content is invalid.
    """

    # noinspection PyTypeHints
    @classmethod
    @lru_cache
    def is_validator(cls, validator: Any) -> TypeIs[IValidator]:  # noqa: ANN401
        """
        Ensure that the given object is a valid validator.

        Valid validator is a callable class inheriting from BaseValidator, or a function with the signature
        `Callable[[str, Tag], None]`.

        Args:
            validator (Any): The object to check.

        Returns:
            TypeIs[IValidator]: True if the object is a valid validator, False otherwise.
        """
        if isinstance(validator, cls):
            return True

        return has_same_signature(validator, cls.__call__)

    @abc.abstractmethod
    def __call__(self, content: str, tag: Tag) -> None:
        """
        Implementation of the validation logic.

        Args:
            content (str): The template string or substring to validate.
            tag (Tag): The tag instance that specify the tag specification.

        Raises:
            TemplateValidationError: If the content is invalid.
        """


class NoopValidator(BaseValidator):
    """A validator that does nothing."""

    def __call__(self, content: str, tag: Tag) -> None:
        """Do nothing."""


class ChainValidator(BaseValidator):
    """
    A validator that chains multiple validators together.

    This validator will run all the validators in the order they were provided.

    Args:
        *validators (BaseValidator): The validators to chain together.
    """

    def __init__(self, *validators: IValidator) -> None:
        self._validators: tuple[IValidator, ...] = tuple(validators)

    def __call__(self, content: str, tag: Tag) -> None:
        """
        Apply specified validators to the content.

        Args:
            content (str): The template string or substring to validate.
            tag (Tag): The tag instance that specify the tag specification.

        Raises:
            TemplateValidationError: If the content is invalid.
        """  # noqa: DOC502
        for validator in self._validators:
            validator(content, tag)


@dataclasses.dataclass(slots=True, frozen=True)
class TagCodec:
    """An interface to access the encoder and decoder objects for a specific tag and format."""

    encoder: IEncoder
    """
    The encoder object that transform the content from an original template string to a target format.

    Can be instance of `BaseEncoder` or a function with the signature `Callable[[str, Tag], str]`.
    """
    decoder: IDecoder | None = None
    """
    The decoder object that transform the content from a target format to an original template string.

    Can be instance of `BaseDecoder` or a function with the signature `Callable[[str, Tag], str]`.
    """
    validator: IValidator = dataclasses.field(default_factory=NoopValidator)
    """
    The validator object that checks if the content is valid for the specified tag.

    Can be instance of `BaseValidator` or a function with the signature `Callable[[str, Tag], None]`.
    """

    def encode(self, content: str, tag: Tag) -> str:
        """
        Encode the content using the encoder object.

        Args:
            content (str): The template string or substring to encode.
            tag (Tag): The tag object that specifies the transformation rules.

        Returns:
            str: Encoded content.
        """
        return self.encoder(content, tag)

    def decode(self, content: str, tag: Tag) -> str:
        """
        Decode the content using the decoder object.

        Args:
            content (str): The encoded content to decode.
            tag (Tag): The tag object that specifies the transformation rules.

        Returns:
            str: Decoded content.

        Raises:
            DecoderIsNotProvidedError: If the decoder object is not provided.
        """
        if self.decoder is None:
            msg = "This codec does not support decoding."
            raise DecoderIsNotProvidedError(msg)

        return self.decoder(content, tag)

    def validate(self, content: str, tag: Tag) -> None:
        """
        Validate the content using the validator object.

        Args:
            content (str): The template string or substring to validate.
            tag (Tag): The tag object that specifies the transformation rules.

        Raises:
            TemplateValidationError: If the content is invalid.
        """  # noqa: DOC502
        return self.validator(content, tag)
