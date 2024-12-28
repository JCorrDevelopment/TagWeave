from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from tag_weave.errors import TagIsInvalidError, TagMappingAlreadyExistsError

if TYPE_CHECKING:
    from collections.abc import Mapping


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
    _known_mappings: dict[str, tuple[str, str | None]] = dataclasses.field(
        default_factory=dict[str, tuple[str, str | None]], init=False
    )
    """
    Mapping between the target template encoding format and the corresponding start and end blocks in that format.

    As well, this mapping may be used in reverse order to decode the template string back from the target format.
    This field is not populated automatically, and should be explicitly populated using `set_mapping`, `update_mapping`
    or `remove_mapping` methods.

    Access to this field is restricted to the access methods as well, such as `get_mapping`, `list_mapping`, etc.
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

    def set_mapping(self, target_format: str, target_tags: tuple[str, str | None], *, replace: bool = False) -> None:
        """
        Set the mapping between the target template encoding format and the start and end blocks in that format.

        Args:
            target_format (str): The target template encoding format.
            target_tags (tuple[str, str| None]): The start and end blocks in the target format.
            replace (bool): If True, the mapping will be updated in place, otherwise a new object will be created.

        Raises:
            TagMappingAlreadyExistsError: If the target format is already mapped to another start and end blocks.
        """
        if not replace and target_format in self._known_mappings:
            msg = f"Mapping for the target format '{target_format}' already exists."
            raise TagMappingAlreadyExistsError(msg)

        self._known_mappings[target_format] = target_tags

    def update_mapping(self, updates: Mapping[str, tuple[str, str | None]], *, replace: bool = False) -> None:
        """
        Update the mapping with the new values.

        Args:
            updates (Mapping[str, tuple[str, str | None]]): The mapping to update with.
            replace (bool): If True, the mapping will be updated in place, otherwise a new object will be created.

        Raises:
            TagMappingAlreadyExistsError: If the target format is already mapped to another start and end blocks.
        """
        if not replace and any(target_format in self._known_mappings for target_format in updates):
            msg = "Some of the target formats are already mapped."
            raise TagMappingAlreadyExistsError(msg)

        self._known_mappings.update(dict(updates))

    def replace_mapping(self, new: Mapping[str, tuple[str, str | None]]) -> None:
        """
        Replace the mapping with the new values.

        Args:
            new (Mapping[str, tuple[str, str | None]]): The target template encoding format.
        """
        self._known_mappings = dict(new)

    def get_target_format_tags(self, target_format: str) -> tuple[str, str | None] | None:
        """
        Get the start and end tags in the target format.

        Args:
            target_format (str): The target template encoding format.

        Returns:
            tuple[str, str | None] | None: The start and end tags in the target format. If the target format is not
                mapped, returns None.
        """
        return self._known_mappings.get(target_format)
