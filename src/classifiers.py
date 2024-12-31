from typing import Union, List, Dict
from textChunker import TextChunk
from chatter import Chatter
from prompts import about_china
import os
import re
import json

cn_words = {
    'China',
    'zhonguo',
    '中国'
}


def extract_json_content(text):
    # 正则表达式模式，非贪婪匹配以获取最短的符合条件的字符串
    pattern = r'```json\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)  # re.DOTALL使.可以匹配换行符
    if match:
        return match.group(1)  # 返回匹配到的第一个捕获组，即括号内的内容
    else:
        return None  # 如果没有找到匹配的内容，则返回None


class CN:
    def __init__(self, lm_name=None):
        if lm_name:
            self.chatter=Chatter(lm_name)
        else:
            self.chatter=None
        self.lm_loaded=False
    
    def load_lm(self, ):
        if self.lm_loaded:
            return
        try:
            self.chatter.load_model()
        except Exception as e:
            print(f"ERROR IN LOAD LM \n {e}")
            return
        self.lm_loaded=True

    def hard_cls(self, chunk: TextChunk):
        s = str(chunk)
        for w in cn_words:
            if w in s:
                return True
        return False
    
    def lm_cls(self, chunk: TextChunk):
        if not self.lm_loaded:
            self.load_lm()
        chunks = [str(chunk)]

        # chunks = chunks[:25]
        # querys = [about_china+c for c in chunks]
        # pprint(querys)
        messages = [[
            {
                "role": "system",
                "content": about_china
            },
            {
                "role": "user",
                "content": c
            }
        ] for c in chunks]
        # results = chatter.generate(querys)
        sampling_params={
            'n': 1,
            'max_tokens': 100,
            'min_tokens': 1,
            
        }
        results = self.chatter.chat(messages, sampling_params)
        # pprint(results) 
        results = [extract_json_content(r) for r in results]
        for i, r in enumerate(results):
            try:
                results[i] = json.loads(r)
            except Exception as e:
                print(e)
                results[i] = {'raw_str': r}
        return results


    def cls(self, chunk: TextChunk):

        if self.hard_cls(chunk):
            return {
            "是否有关中国": "是",
            "理由": "含有关键字"
            }
        return self.lm_cls(chunk)

if __name__ == '__main__':
    from pathlib import Path
    from textChunker import Article, article_from_txt, chunks_from_article
    from pprint import pprint
    model_name = "Qwen2.5-7B-Instruct"
    # chatter = Chatter(model_name)
    # chatter.load_model()
    test_dir = Path('/home/admin2024/repos/chacls/test_data')
    article_list: List[Article] = [
        article_from_txt(test_dir/fn) for fn in os.listdir(test_dir)
    ]

    text_chunks: List[TextChunk] = sum([
        chunks_from_article(x) for x in article_list
    ], [])
    print(f"{len(text_chunks)=}")
    for chunk in text_chunks[:25]:
        print(chunk)
    # text_chunks = text_chunks[:25]

    classifier = CN(model_name)
    results = [classifier.cls(c) for c in text_chunks]
    pprint(results)
