from __future__ import annotations

import abc
import dataclasses
from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypeIs

from twilight_utils.more_typing.signatures import has_same_signature

from tag_weave.errors import EncoderAlreadySetError, TagIsInvalidError


class BaseEncoder(abc.ABC):
    """Base class for a class-based encoders."""

    @abc.abstractmethod
    def __call__(self, content: str, tag: Tag) -> str:
        """
        Encode the content of a tag into a target format.

        Args:
            content (str): The raw content of the tag.
            tag (Tag): The tag instance that contains the content.

        Returns:
            str: The encoded content of the tag.
        """

    @classmethod
    @lru_cache
    def is_encoder(cls, encoder: Any) -> bool:  # noqa: ANN401
        """Check if the given encoder matches the expected signature of IEncoder.__call__.

        Args:
            encoder (Callable): The encoder function or callable object to check.

        Returns:
            bool: True if the encoder matches the expected signature, False otherwise.
        """
        if isinstance(encoder, cls):
            return True

        return has_same_signature(encoder, cls.__call__)


class BaseValidator(abc.ABC):
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

    def __init__(self, *validators: BaseValidator) -> None:
        self._validators: tuple[BaseValidator, ...] = tuple(validators)

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


type IValidator = BaseValidator | Callable[[str, Tag], None]
"""
Type alias for a validator object.

Used to simplify type hints and improve readability. Shows that the object should be either a class-based validator
or a function with the signature `Callable[[str, Tag], None]`.
"""
type IEncoder = BaseEncoder | Callable[[str, Tag], str]
"""
Type alias for an encoder object.

Used to simplify type hints and improve readability. Shows that the object should be either a class-based encoder
or a function with the signature `Callable[[str, Tag], str]`.
"""


@dataclasses.dataclass(slots=True)
class Tag:
    """Define required methods and behavior of a tag instance."""

    name: str
    """
    The name of the tag

    This name it used to simplify string representation of the tag instance and may help to improve logging
    and documentation readability.

    In real implementation, it is expected not to use this field for runtime logic.
    """
    start: str
    """
    A string representing the start of the tag.

    This string is used to identify the beginning of the tag substring in the template string. Everything after
    this and before the correct `end` string is considered the content of the tag and may be processed according
    to specified codecs.
    """
    end: str | None = dataclasses.field(default=None)
    """
    A string representing the end of the tag.

    This string is used to identify the end of the tag substring in the template string. Everything after the
    `start` string and before this string is considered the content of the tag and may be processed according to
    specified codecs.

    Is block is `self_closing`, than this field is not required. Otherwise, TagIsInvalidError is raised.
    """

    self_closing: bool = False
    """
    Indicates whether the tag is self-closing or not.

    If True, the tag does not require an `end` string, and it itself is considered as full substring of the template.
    """
    allows_children: bool = True
    """
    Indicates that the tag may contain nested tags other than itself.
    """
    allows_self_nesting: bool = False
    """
    Indicates that the tag may contain itself as a nested tag.

    Good example of this behaviour is the `<dev>` tag in HTML markup language, which may contain other `<dev>` tags
    inside.
    """

    description: str | None = dataclasses.field(default=None)
    """
    Optional human-readable description of the tag.

    Useful for documentation and debugging purposes. Expected not to be used for runtime logic.
    """

    _is_single_tag: bool = dataclasses.field(default=False, init=False)
    """
    Indicated that start and end strings are the same.

    This field is calculated automatically based on `start` and `end` fields during __post_init__ method.
    """

    _validator: IValidator = dataclasses.field(init=False)
    """
    List of validators that should be applied to the tag content before encoding.
    """
    _encoders: dict[str, IEncoder] = dataclasses.field(default_factory=dict[str, IEncoder], init=False)
    """
    Dictionary of encoders that should be applied to the tag content before encoding.

    Key of the dictionary is the name of target format, and value is the codec object that should be used to encode.
    """

    def __post_init__(self) -> None:
        """
        Provide additional and calculated fields initialization during the object creation.

        Raises:
            TagIsInvalidError: If the tag is not self-closing and the end string is not provided.
        """
        if not self.self_closing and self.end is None:
            msg = "End tag is required for non-self-closing tags."
            raise TagIsInvalidError(msg)

        self._is_single_tag = self.start == self.end

        self._validator = NoopValidator()
        self._encoders = dict[str, IEncoder]()

    @property
    def is_single_tag(self) -> bool:
        """
        Indicated that start and end strings are the same.

        This field is calculated automatically based on `start` and `end` fields during __post_init__ method.
        """
        return self._is_single_tag

    def set_validator(self, validator: IValidator) -> None:
        """
        Set the validator for the tag.

        Args:
            validator (IValidator): The validator to set.
        """
        self._validator = validator

    def add_encoder(self, target_format: str, encoder: IEncoder, *, replace: bool = False) -> None:
        """
        Add encoder to the tag for the target template format.

        Args:
            target_format (str): The name of the target format to encode the tag content.
            encoder (IEncoder): The encoder object to use for encoding.
            replace (bool): if False, the EncoderAlreadySetError is raised if the encoder for the target format
                is already set.

        Raises:
            EncoderAlreadySetError: If the encoder for the target format is already set and `replace` is False.
        """
        if not replace and target_format in self._encoders:
            msg = f"Encoder for the target format {target_format!r} is already set."
            raise EncoderAlreadySetError(msg)

        self._encoders[target_format] = encoder

    def update_encoders(self, encoders: dict[str, IEncoder], *, replace: bool = False) -> None:
        """
        Update the encoders for the tag.

        If at least one encoder is already set and `replace` is False, the EncoderAlreadySetError is raised without
        updating any encoders.

        Args:
            encoders (dict[str, IEncoder]): The dictionary of encoders to set.
            replace (bool): if False, the EncoderAlreadySetError is raised if the encoder for the target format
                is already set.

        Raises:
            EncoderAlreadySetError: If the encoder for the target format is already set and `replace` is False.
        """
        if not replace and any(target_format in self._encoders for target_format in encoders):
            msg = "Some encoders are already set."
            raise EncoderAlreadySetError(msg)

        self._encoders.update(encoders)

    def replace_encoders(self, encoders: dict[str, IEncoder]) -> None:
        """
        Replace the encoders for the tag.

        Args:
            encoders (dict[str, IEncoder]): The dictionary of encoders to set.
        """
        self._encoders = encoders
