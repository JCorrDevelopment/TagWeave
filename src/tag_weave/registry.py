from __future__ import annotations

from typing import Any, NamedTuple, Self

from .tag import Tag
from .tag_codecs import BaseDecoder, BaseEncoder, TagCodec
from .tag_codecs.base import BaseValidator, ChainValidator, IValidator, NoopValidator


class _TagSpec(NamedTuple):
    codec: dict[str, TagCodec]
    validator: IValidator


class TagRegistry:
    """A registry containing all the tags defined for dedicated use as a template string."""

    def __init__(self) -> None:
        self._codecs: dict[Tag, _TagSpec] = {}

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> Self:
        """
        Create a new instance of the registry from a configuration dictionary.

        Args:
            config: The configuration dictionary to create the registry from.

        Returns:
            Self: The new instance of the registry.
        """
        registry = cls()
        for tag_config in config["tags"]:
            codecs_spec = tag_config.pop("codecs", {})
            validators_spec = tag_config.pop("validators", [])
            tag = Tag(**tag_config)
            validator = registry._initialize_validators(validators_spec)
            codecs = registry._initialize_codecs(codecs_spec)
            tag_spec = _TagSpec(codecs, validator)
            registry.add_tag(tag, tag_spec)
        return registry

    @classmethod
    def _initialize_codecs(cls, codecs_config: dict[str, dict[str, str]]) -> dict[str, TagCodec]:
        """
        Initialize the codecs from a configuration dictionary.

        Args:
            codecs_config (dict[str, CodecSpec]): The configuration dictionary to initialize the codecs from.

        Returns:
            dict[str, TagCodec]: The initialized codecs.
        """
        codecs = {}
        for format_, codec_spec in codecs_config.items():
            tag_codec = TagCodec(
                encoder=(BaseEncoder.by_import_str(codec_spec["encoder"])),
                decoder=(BaseDecoder.by_import_str(decoder_str))
                if (decoder_str := codec_spec.get("decoder"))
                else None,
            )
            codecs[format_] = tag_codec
        return codecs

    def _initialize_validators(self, validators_config: list[str]) -> IValidator:
        """
        Initialize the validators from a configuration list.

        Args:
            validators_config (list[str]): The configuration list to initialize the validators from.

        Returns:
            IValidator: The initialized validators.
        """
        if len(validators_config) == 0:
            return NoopValidator()
        if len(validators_config) == 1:
            return BaseValidator.by_import_str(validators_config[0])
        return ChainValidator(*[BaseValidator.by_import_str(validator_str) for validator_str in validators_config])

    def add_tag(self, tag: Tag, tag_spec: _TagSpec) -> None:
        """
        Add a new tag to the registry.

        Args:
            tag (Tag): The tag to add.
            tag_spec (_TagSpec): The codecs to add.
        """
        self._codecs[tag] = tag_spec

    def list_validators(self) -> list[tuple[Tag, IValidator]]:
        """
        List all the tags and their validators in the registry.

        Returns:
            list[Tag, list[IValidator]]: The list of tags and their validators.
        """
        return [(tag, tag_spec.validator) for tag, tag_spec in self._codecs.items()]

    def list_codecs(self, format_: str) -> list[tuple[Tag, TagCodec]]:
        """
        List all the tags and their codecs in the registry for a specific format.

        Args:
            format_ (str): The format to list the codecs for.

        Returns:
            list[Tag, TagCodec]: The list of tags and their codecs.
        """
        return [(tag, tag_spec.codec[format_]) for tag, tag_spec in self._codecs.items()]
