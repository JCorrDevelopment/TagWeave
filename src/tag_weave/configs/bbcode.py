BB_CODE_CONFIG = {
    "tags": [
        {
            "start": "[b]",
            "end": "[/b]",
            "name": "bold",
            "description": "Makes specified text bold.",
            "codecs": {
                "html": {
                    "encoder": "tag_weave.tag_codecs.bbcode.html.BbCodeBoltHtmlEncoder",
                },
            },
            "validators": [
                "tag_weave.tag_codecs.bbcode.validators.TagCorrectlyClosed",
            ],
        },
        {
            "start": "[i]",
            "end": "[/i]",
            "name": "italic",
            "description": "Makes specified text italic.",
            "codecs": {
                "html": {
                    "encoder": "tag_weave.tag_codecs.bbcode.html.BbCodeItalicHtmlEncoder",
                },
            },
            "validators": [
                "tag_weave.tag_codecs.bbcode.validators.TagCorrectlyClosed",
            ],
        },
        {
            "start": "[u]",
            "end": "[/u]",
            "name": "underline",
            "description": "Underlines specified text.",
            "codecs": {
                "html": {
                    "encoder": "tag_weave.tag_codecs.bbcode.html.BbCodeUnderlineHtmlEncoder",
                },
            },
            "validators": [
                "tag_weave.tag_codecs.bbcode.validators.TagCorrectlyClosed",
            ],
        },
    ]
}
