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
        }
    ]
}
