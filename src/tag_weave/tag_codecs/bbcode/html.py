# noqa: A005
import abc

from tag_weave.errors import IncorrectEncoderError
from tag_weave.tag import Tag

from ..base import BaseEncoder


class _BbCodeBaseHtmlEncoder(BaseEncoder, abc.ABC):
    def __init__(self, html_start: str, html_end: str) -> None:
        self._html_start = html_start
        self._html_end = html_end

    def __call__(self, content: str, tag: Tag) -> str:
        if tag.end is None:
            msg = f"Encoder {self.__class__!r} cannot be applied to tag {tag!r} because it is self-closing."
            raise IncorrectEncoderError(msg)
        return content.replace(tag.start, self._html_start).replace(tag.end, self._html_end)


class BbCodeBoltHtmlEncoder(_BbCodeBaseHtmlEncoder):
    """
    Encode specified BBCode template bold tag (`[b]...[/b]`) to HTML format.

    Examples:
            >>> encoder = BbCodeBoltHtmlEncoder()
            >>> encoder("[b]Hello, World![/b]", Tag(start="[b]", end="[/b]", name="bold"))
            '<strong>Hello, World!</strong>'
    """

    def __init__(self) -> None:
        super().__init__(html_start="<strong>", html_end="</strong>")
