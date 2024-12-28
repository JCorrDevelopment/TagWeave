from tag_weave.errors import IncorrectValidatorError, TemplateValidationError
from tag_weave.tag import Tag
from tag_weave.tag_codecs.base import BaseValidator


class TagCorrectlyClosed(BaseValidator):
    """A validator that checks if a tag is correctly closed."""

    def __call__(self, content: str, tag: Tag) -> None:
        """
        Check that all opened tags are explicitly closed.

        Args:
            content (str): The template string or substring to validate.
            tag (Tag): The tag instance that specify the tag specification.

        Raises:
            TemplateValidationError: If the tag is not correctly closed.
            IncorrectValidatorError: If the tag is self-closing.
        """
        if tag.end is None:
            msg = f"Validator {self.__class__!r} cannot be applied to tag {tag!r} because it is self-closing."
            raise IncorrectValidatorError(msg)
        opened_tags = []
        len_start = len(tag.start)
        len_end = len(tag.end)

        for i in range(len(content)):
            if content[i : i + len_start] == tag.start:
                opened_tags.append(i)
            elif content[i : i + len_end] == tag.end:
                if not opened_tags:
                    msg = f"Tag '{tag.start}' is not correctly closed."
                    raise TemplateValidationError(msg)
                opened_tags.pop()
        if opened_tags:
            msg = f"Tag '{tag.start}' is not correctly closed."
            raise TemplateValidationError(msg)
