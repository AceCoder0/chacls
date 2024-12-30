from typing import Union, List, Dict
from textChunker import TextChunk


cn_words = {
    'China',
    'zhonguo',
    '中国'
}


class CN:
    def __init__(self):
        pass

    def hard_cls(self, chunk: TextChunk):
        s = str(chunk)
        for w in cn_words:
            if w in s:
                return True
        return False
    