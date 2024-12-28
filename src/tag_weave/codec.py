from __future__ import annotations

__all__ = ["BaseDecoder", "BaseEncoder", "Codec", "IDecoder", "IEncoder"]

import abc
import dataclasses
from collections.abc import Callable
from functools import lru_cache
from typing import Any, TypeIs

from twilight_utils.more_typing.signatures import has_same_signature

from tag_weave.errors import DecoderIsNotProvidedError
from tag_weave.tag import Tag


class _BaseTransformer(abc.ABC):
    """Base class that specified the interface for an object transformation, such as template encoders and decoders."""

    @abc.abstractmethod
    def __call__(self, content: str, tag: Tag, format_: str) -> str:
        """
        Transform the string by rules specified in the tag object and provided format_ parameter.

        Args:
            content (str): string or a substring to transform
            tag (Tag): tag object that contains the transformation rules
            format_ (str): format of the content

        Returns:
            str: transformed content
        """


class BaseEncoder(_BaseTransformer, abc.ABC):
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


class BaseDecoder(_BaseTransformer, abc.ABC):
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


type IDecoder = BaseDecoder | Callable[[str, Tag, str], str]
"""
Type alias for an decoder object.

Used to simplify type hints and improve readability. Shows that the object should be either a class-based decoder
or a function with the signature `Callable[[str, Tag, str], str]`.

Decoders are supposed only to transform the content from an encoded format to target, but not to validate it.
Validation should be done before decoding the content or be assumed to be valid beforehand.
"""
type IEncoder = BaseEncoder | Callable[[str, Tag, str], str]
"""
Type alias for an encoder object.

Used to simplify type hints and improve readability. Shows that the object should be either a class-based encoder
or a function with the signature `Callable[[str, Tag, str], str]`.

Encoders are supposed only to transform the content from an original template string to a target format, but not to
validate it. Before encoding the content, collection of tag validators should be applied to ensure that the content
is, in face, a valid template string according to registry rules.
"""


@dataclasses.dataclass(slots=True, frozen=True)
class Codec:
    """An interface to access the encoder and decoder objects for a specific tag and format."""

    encoder: IEncoder
    """
    The encoder object that transform the content from an original template string to a target format.

    Can be instance of `BaseEncoder` or a function with the signature `Callable[[str, Tag, str], str]`.
    """
    format_: str
    """
    The target format of the content this codec is supposed to transform.
    """
    decoder: IDecoder | None = None
    """
    The decoder object that transform the content from a target format to an original template string.

    Can be instance of `BaseDecoder` or a function with the signature `Callable[[str, Tag, str], str]`.
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
        return self.encoder(content, tag, self.format_)

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

        return self.decoder(content, tag, self.format_)
