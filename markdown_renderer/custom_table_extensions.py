import re

from markdown.blockprocessors import BlockProcessor
from markdown.extensions import Extension
from markdown.extensions.tables import TableProcessor
import xml.etree.ElementTree as etree


class CustomTableProcessor(BlockProcessor):
    """ <thead> 없이도 테이블을 렌더링하도록 확장 """

    TABLE_RE = re.compile(r'^\|(.+?)\|$')  # 테이블 행을 인식하는 정규식
    CELL_SPLIT_RE = re.compile(r'\s*\|\s*')  # 셀을 분할하는 정규식

    def test(self, parent, block):
        """ 블록이 테이블인지 확인 """
        return bool(self.TABLE_RE.match(block.strip()))

    def run(self, parent, blocks):
        """ 블록을 <table> 요소로 변환 """
        table = etree.SubElement(parent, "table")
        tbody = etree.SubElement(table, "tbody")  # <thead> 없이 <tbody>만 추가

        while blocks:
            block = blocks.pop(0).strip()
            if not self.TABLE_RE.match(block):
                blocks.insert(0, block)  # 테이블이 아니면 다시 블록 리스트에 추가하고 종료
                break

            tr = etree.SubElement(tbody, "tr")  # <tr> 생성
            cells = self.CELL_SPLIT_RE.split(block.strip('|'))  # 셀 분할
            for cell in cells:
                td = etree.SubElement(tr, "td")  # <td> 생성
                td.text = cell.strip()

class CustomTableExtension(Extension):
    """ <thead> 없이 테이블을 지원하는 Markdown 확장 """

    def extendMarkdown(self, md):
        """ Markdown 파서에 커스텀 테이블 프로세서 추가 """
        md.parser.blockprocessors.register(CustomTableProcessor(md.parser), "custom_table", 75)