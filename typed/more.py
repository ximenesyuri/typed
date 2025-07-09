from typed.mods.decorators         import typed
from typed.mods.factories.base     import Union, Null
from typed.mods.factories.generics import Filter, Regex
from typed.mods.types.base         import Str
from typed.mods.helper.more        import (
    _is_markdown,
    _is_pure_markdown
)

Markdown = Filter(Str, typed(_is_markdown))
PureMarkdown = Filter(Str, typed(_is_pure_markdown))

Markdown.__display__ = "Markdown"
PureMarkdown.__display__ = "PureMarkdown"

RclonePath = Union(Regex(r'^([^/:\r\n*?\"<>|\\]+:/??|(?:[^/:\r\n*?\"<>|\\]+:)?(?:/?(?:[^/:\r\n*?\"<>|\\]+/)*[^/:\r\n*?\"<>|\\]+/?))$'), Null(Str))
RclonePath.__display__ = "RclonePath"
