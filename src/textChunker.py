import os
import sys
import json
import pandas as pd
from pathlib import Path
from collections import namedtuple
from typing import List, Union
from tqdm import tqdm
import random


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
    def __init__(
            self, 
            title: str, 
            source: str, 
            ttime: str, 
            paragraphs: List[str], 
            url: Url=None, 
            author=None
        ):
        self.title = title
        self.source = source
        self.ttime = ttime
        self.paragraphs = paragraphs
        self.url = url
        self.author = author
    
    def __str__(self):
        return f"{self.title=}, {self.source=}, {self.ttime=}, {self.url=}"
    
    def get_dict(self):
        return {
            "title": self.title,
            "source": self.source,
            "ttime": self.ttime,
            "author": self.author,
            "url": str(self.url),
            
        }

    def get_content(self):
        return "\n\n".join(self.paragraphs)
    

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
            "content": self.article.get_content(),
            **self.article.get_dict()
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

def article_from_json(json_path: Path):
    with open(json_path, 'r', encoding='utf-8') as f:
        json_dict = json.load(f)
    title = json_dict['title']
    author = json_dict['author'].split('\n')[0]
    # source = json_dict['source']
    source=None
    ttime = json_dict['publish_time']
    article = json_dict['content']
    paragraphs = article.split('\n\n')
    url = json_path.stem
    return Article(
        title=title,
        source=source,
        ttime=ttime,
        paragraphs=paragraphs, 
        url=url,
        author=author
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


def process_zaobao_sample(samples_dir, dest_dir):
    samples_dir = Path(samples_dir)
    articles = []
    for fn in tqdm(os.listdir(samples_dir)):
        if fn.endswith('.json'):
            articles.append(article_from_json(samples_dir/fn))
    all_chunks: List[List[TextChunk]] = [chunks_from_article(a) for a in articles]

    chunks = []
    for chunk_list in all_chunks:
        c1 = ""
        n=0
        while not str(c1) and n<5:
            c1 = random.choice(chunk_list)
            n += 1
        chunks.append(c1)
        # while not str()
    jsonl_path = dest_dir / "chunks.jsonl"
    excel_path = dest_dir / "chunks.xlsx"
    save_chunks(chunks, jsonl_path, excel_path)
    label_excel_dir = dest_dir / "label_excel"
    os.makedirs(label_excel_dir, exist_ok=True)
    # use save_chunks to save chunks to excels. each has 100 lines
    for i in range(0, len(chunks), 100):
        save_chunks(chunks[i:i+100], None, label_excel_dir / f"chunks_{i}.xlsx")
    # return chunks

if __name__ == '__main__':
    # test()

    samples_dir = Path("/mnt/ecf82360-d01d-4966-b234-c47ea01078db/datas1224/https--www-zaobao-com-/parsed")
    dest_dir = Path("/mnt/ecf82360-d01d-4966-b234-c47ea01078db/datas1224/https--www-zaobao-com-/chunks_sampled0119")
    os.makedirs(dest_dir, exist_ok=True)
    process_zaobao_sample(samples_dir, dest_dir)

