from __future__ import annotations

import abc
from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypeIs

from twilight_utils.more_typing.signatures import has_same_signature

from tag_weave.tag import Tag


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


type IValidator = BaseValidator | Callable[[str, Tag], None]
"""
Type alias for a validator object.

Used to simplify type hints and improve readability. Shows that the object should be either a class-based validator
or a function with the signature `Callable[[str, Tag], None]`.
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
