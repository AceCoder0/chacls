import os
import sys
import json
import pandas as pd
from pathlib import Path
from collections import namedtuple
from typing import List, Union


# Chunk = namedtuple('Chunk', ['text', 'title', 'writer', 'src', 'time'])
class Url:
    def __init__(self, address: str, base_site: str, level: int = -1, parent: 'Url' =None):
        self.address: str = address
        self.base_site: str = base_site
        self.level: str = level
        self.parent: Url = parent
    
    def __str__(self):
        return self.address
    

class Article:
    def __init__(self, title: str, source: str, ttime: str, paragraphs: List[str], url: Url=None):
        self.title = title
        self.source = source
        self.ttime = ttime
        self.paragraphs = paragraphs
        self.url = url
    
    def __str__(self):
        return f"{self.title=}, {self.source=}, {self.ttime=}, {self.url=}"
    
    def get_dict(self):
        return {
            "title": self.title,
            "source": self.source,
            "ttime": self.ttime,
            "url": str(self.url)
        }
    

class TextChunk:
    def __init__(self, text_str: str, article: Article):
        self.text_str: str = text_str
        self.article: Article = article
    
    def get_url(self) -> Url:
        return self.article.url

    def __str__(self):
        return self.text_str
    
    def __repr__(self):
        return self.text_str

    def get_dict(self):
        return {
            "text_str": str(self),
            "article": self.article.get_dict()
        }

    
def article_from_txt(txt_path, url=None):
    # print(txt_path)
    with open(txt_path, 'r', encoding='utf-8') as f:
        txt_str = f.read()
    txts: List[str] = txt_str.split('\n\n\n')
    
    title: str = txts[0]
    source: str = txts[1]
    ttime: str = txts[2]
    text: str = txts[3]
    paragraphs: List[str] = text.split('\n\n')
    return Article(
        title=title,
        source=source,
        ttime=ttime,
        paragraphs=paragraphs, 
        url=url
    )

def chunks_from_article(article: Article) -> List[TextChunk]:
    return [TextChunk(x, article) for x in article.paragraphs]

def save_chunks(
    chunks: List[TextChunk],
    jsonl_path: Union[str, Path] =None,
    excel_path: Union[str, Path]= None
):
    if (jsonl_path is None) and (excel_path is None):
        raise ValueError("must provide a save_path")
    if jsonl_path:
        with open(jsonl_path, 'a', encoding='utf-8') as f:
            for chunk in chunks:
                json_str = json.dumps(chunk.get_dict(), ensure_ascii=False)
                f.write(json_str+'\n')
    
    if excel_path:
        items = [c.get_dict() for c in chunks]
        df = pd.DataFrame(items)
        df.to_excel(excel_path, index=False)

def test():
    test_dir = Path('/home/admin2024/repos/chacls/test_data')
    article_list: List[Article] = [
        article_from_txt(test_dir/fn) for fn in os.listdir(test_dir)
    ]

    text_chunks: List[TextChunk] = sum([
        chunks_from_article(x) for x in article_list
    ], [])
    print(f"{len(text_chunks)=}")
    for chunk in text_chunks[:5]:
        print(chunk)

if __name__ == '__main__':
    test()