import os
from vllm import LLM, SamplingParams
from llm_path import llm_path
from typing import Dict, Union, List
from transformers import AutoTokenizer
from pathlib import Path
from textChunker import (
    Article,
    article_from_txt,
    chunks_from_article,
    TextChunk
)
from prompts import about_china
from pprint import pprint


class Chatter:
    def __init__(self, model_name: str, sampling_params: Dict=None):
        self.model_name=model_name
        self.llm = None
        self.tokenizer=None
        self.model_loaded=False
        self.model_path = llm_path[model_name]
        if sampling_params:
            self.sampling_params=SamplingParams(**sampling_params)
        else:
            self.sampling_params=SamplingParams(n=1)

    def load_model(self):
        self.llm = LLM(self.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model_loaded=True
    
    def set_sampling_params(self, sampling_params: Union[Dict, SamplingParams]):
        if isinstance(sampling_params, SamplingParams):
            self.sampling_params = sampling_params
        else:
            self.sampling_params = SamplingParams(**sampling_params)

    def generate(self, prompt: Union[str, List[str]], sampling_params: Union[Dict, SamplingParams]=None) -> Union[str, List[str]]:
        assert self.model_loaded, f"llm must be loaded before generate."
        if sampling_params:
            self.set_sampling_params(sampling_params) 
        response = self.llm.generate(prompt, sampling_params=self.sampling_params)
        response = [o.outputs[0].text for o in response]
        if isinstance(prompt, list):
            return response
        return response[0]
        
    def chat(self, prompts: Union[List[str], str, Dict], sampling_params: Dict=None) -> List[str]:
        # if isinstance(prompts, Dict):
        prompts = self.tokenizer.apply_chat_template(
            prompts,
            add_generation_prompt=True,
            tokenize=False
        )
        return  self.generate(prompts, sampling_params)

    def multiturn_chat(self,):
        pass


# class 


def test():
    model_name = "Qwen2.5-3B-Instruct"
    chatter = Chatter(model_name)
    chatter.load_model()
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
    
    chunks: List[str] = [str(x) for x in text_chunks]

    chunks = chunks[:5]
    querys = [about_china+c for c in chunks]
    pprint(querys)
    results = chatter.generate(querys)
    pprint(results)


if __name__=='__main__':
    test()
