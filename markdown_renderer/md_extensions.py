# https://alberand.com/markdown-custom-tags.html
# https://hostman.com/tutorials/how-to-use-python-markdown-to-convert-markdown-to-html/

from markdown.extensions import Extension
from markdown.blockprocessors import BlockProcessor

import re
import xml.etree.ElementTree as etree

from markdown.inlinepatterns import LinkInlineProcessor


class ImageInlineProcessor(LinkInlineProcessor):
    """ Return a img element from the given match. """

    def handleMatch(self, m, data):
        text, index, handled = self.getText(data, m.end(0))
        if not handled:
            return None, None, None

        src, title, index, handled = self.getLink(data, index)
        if not handled:
            return None, None, None

        div = etree.Element("div")
        div.set("class", "image-container")

        a = etree.SubElement(div, "a")
        a.set("href", src)

        img = etree.SubElement(a, "img")

        img.set("src", src)

        if title is not None:
            img.set("title", title)

        img.set('alt', self.unescape(text))

        return div, m.start(0), index


class Comments(BlockProcessor):
    RE_FENCE_START = r'^\[([a-zA-Z0-9_-]{3,})\]: '  # [alberand]:

    def test(self, parent, block):
        return re.match(self.RE_FENCE_START, block)

    def run(self, parent, blocks):
        blocks[0] = re.sub(self.RE_FENCE_START, '', blocks[0])

        e = etree.SubElement(parent, 'div')
        e.set('class', 'comment')
        self.parser.parseChunk(e, blocks[0])
        blocks.pop(0)

        return True


IMAGE_LINK_RE = r'\!\['


class AlberandTagsExtension(Extension):
    def extendMarkdown(self, md):
        md.parser.blockprocessors.register(Comments(md.parser), 'comments', 175)

        # Deregister default image processor and replace it with our custom one
        md.inlinePatterns.deregister('image_link')
        md.inlinePatterns.register(
            ImageInlineProcessor(IMAGE_LINK_RE, md), 'image_link', 150)