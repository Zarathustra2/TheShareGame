"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""


class MarkdownText:
    """
	Class which contains class methods for creating a markdown text
	"""

    @classmethod
    def link(cls, text, link):
        return f"[{text}]({link}"

    @classmethod
    def heading_one(cls, text):
        return f"# {text}"

    @classmethod
    def heading_two(cls, text):
        return f"## {text}"

    @classmethod
    def heading_three(cls, text):
        return f"### {text}"

    @classmethod
    def italic(cls, text):
        return f"*{text}*"

    @classmethod
    def bold(cls, text):
        return f"**{text}**"
