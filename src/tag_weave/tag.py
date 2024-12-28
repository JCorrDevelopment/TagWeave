from __future__ import annotations

import dataclasses

from tag_weave.errors import TagIsInvalidError


@dataclasses.dataclass(slots=True, unsafe_hash=True)
class Tag:
    """Define required methods and behavior of a tag instance."""

    start: str = dataclasses.field(hash=True)
    """
    A string representing the start of the tag.

    This string is used to identify the beginning of the tag substring in the template string. Everything after
    this and before the correct `end` string is considered the content of the tag and may be processed according
    to specified codecs.

    Start tag required to be unique per registry.
    """
    end: str | None = dataclasses.field(default=None)
    """
    A string representing the end of the tag.

    This string is used to identify the end of the tag substring in the template string. Everything after the
    `start` string and before this string is considered the content of the tag and may be processed according to
    specified codecs.

    Is block is `self_closing`, than this field is not required. Otherwise, TagIsInvalidError is raised.
    """

    name: str | None = dataclasses.field(default=None)
    """
    The name of the tag

    This name it used to simplify string representation of the tag instance and may help to improve logging
    and documentation readability.

    In real implementation, it is expected not to use this field for runtime logic.
    """

    description: str | None = dataclasses.field(default=None)
    """
    Optional human-readable description of the tag.

    Useful for documentation and debugging purposes. Expected not to be used for runtime logic.
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

    _is_single_tag: bool = dataclasses.field(default=False, init=False)
    """
    Indicated that start and end strings are the same.

    This field is calculated automatically based on `start` and `end` fields during __post_init__ method.
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

    @property
    def is_single_tag(self) -> bool:
        """
        Indicated that start and end strings are the same.

        This field is calculated automatically based on `start` and `end` fields during __post_init__ method.
        """
        return self._is_single_tag
