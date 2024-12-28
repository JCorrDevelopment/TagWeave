# noqa: A005
from tag_weave.registry import TagRegistry


class Codec:
    """A codec class that orchestrates the template string validation, encoding and decoding."""

    def __init__(self, registry: TagRegistry) -> None:
        self._registry = registry

    def validate(self, template: str) -> None:
        """
        Validate that template string is valid for specified tag registry.

        Args:
            template (str): The template string to validate.

        Raises:
            TemplateValidationError: If the template string is invalid.
        """  # noqa: DOC502
        for tag, validator in self._registry.list_validators():
            validator(template, tag)

    def encode(self, template: str, format_: str) -> str:
        """
        Encode the template string to the specified format.

        Args:
            template (str): The template string to encode.
            format_ (str): The target format of the encoded string.

        Returns:
            str: Encoded template string.

        Raises:
            TemplateValidationError: If the template string is invalid.
            CodecIsNotProvidedError: If the codec is not provided.
        """  # noqa: DOC502
        self.validate(template)
        for tag, codec in self._registry.list_codecs(format_):
            template = codec.encode(template, tag)

        return template

    def decode(self, template: str, format_: str) -> str:
        """
        Decode the template string from the specified format.

        Args:
            template (str): The template string to decode.
            format_ (str): The target format of the encoded string.

        Returns:
            str: Decoded template string.

        Raises:
            CodecIsNotProvidedError: If the codec is not provided.
            DecoderIsNotProvidedError: If the decoder object is not provided.
        """  # noqa: DOC502
        for tag, codec in self._registry.list_codecs(format_):
            template = codec.decode(template, tag)

        return template
