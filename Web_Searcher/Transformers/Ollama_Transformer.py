import ollama, json, re, unicodedata
from Web_Searcher.Transformers.Transformer import Transformer


class Ollama_Transformer(Transformer):
    def __init__(self):
        self.model_name = "llama3.2:3b"

    def _clean_input_text(self, text):
        """Limpia basura común de extracciones HTML/Scraping"""
        # Eliminar caracteres no imprimibles
        text = self._clean_input_text(text)
        text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
        # Normalizar espacios y eliminar saltos de línea excesivos
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def __extract_triples__(self, text, term):
        # El prompt ahora "inyecta" el término para que el modelo sepa qué buscar
        prompt = f"""
        Extract all knowledge triplets from the text where one of the entities is "{term}".
        Format: [["subject", "relation", "object"], ...]
        Note: Resolve pronouns referring to "{term}".
        Text: {text}
        """

        try:
            response = ollama.generate(model=self.model_name, prompt=prompt)
            raw_content = response['response'].strip()

            # Limpiador de JSON robusto
            match = re.search(r"(\[.*\])", raw_content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return []
        except Exception as e:
            print(f"Error: {e}")
            return []

    def transform(self, text, term):
        # Si el texto es muy largo, lo dividimos en párrafos para mayor precisión
        paragraphs = [p for p in text.split('\n') if len(p.strip()) > 50]
        all_results = []

        for p in paragraphs:
            triples = self.__extract_triples__(p, term)
            all_results.extend(triples)

        return all_results