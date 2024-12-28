"""
Canvas module.

Useful to play with items you're currently working on.

Please, do not commit any changes in this file.
"""

from tag_weave.codecs import Codec
from tag_weave.configs.bbcode import BB_CODE_CONFIG
from tag_weave.registry import TagRegistry


def main() -> None:  # noqa: D103
    # Enter your code here
    bbcode_registry = TagRegistry.from_dict(BB_CODE_CONFIG)
    template_codec = Codec(bbcode_registry)
    test_string = "[b]Hello, World![i] It's some other text[/b] [u]With[/i] underline![/u]"
    result = template_codec.encode(test_string, "html")
    print(result)


if __name__ == "__main__":
    main()
