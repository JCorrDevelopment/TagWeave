from collections import defaultdict
from typing import TYPE_CHECKING

from .codec import Codec

if TYPE_CHECKING:
    from .tag import Tag


class TagRegistry:
    """A registry containing all the tags defined for dedicated use as a template string."""

    def __init__(self) -> None:
        self._codecs: dict[Tag, dict[str, Codec]] = defaultdict(dict[str, Codec])
