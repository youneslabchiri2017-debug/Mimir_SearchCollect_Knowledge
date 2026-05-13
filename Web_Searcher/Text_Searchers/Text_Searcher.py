from Web_Searcher.Transformers.Text_Transformer import Text_Transformer
from Web_Searcher.Transformers.Ollama_Transformer import Ollama_Transformer

class TextSearcher():

    def __init__(self):
        self.transformer = Text_Transformer()
        self.ollama_transformer = Ollama_Transformer()

    def search(self, term):
        pass