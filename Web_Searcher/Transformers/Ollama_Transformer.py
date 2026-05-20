import ollama, json, re, unicodedata
from Web_Searcher.Transformers.Transformer import Transformer


class Ollama_Transformer(Transformer):
    def __init__(self):
        self.model_name = "llama3.2:3b"

        # REGLAS DEL SISTEMA OPTIMIZADAS
        self.system_prompt = {
            "role": "system",
            "content": """You are an expert Data Extraction AI. 
            Your ONLY job is to extract knowledge triplets from the provided text based STRICTLY on the entity requested by the user.

            CRITICAL RULE: The subject (the first element) of EVERY SINGLE TRIPLET must be EXACTLY the requested entity name. Do not use pronouns like "it", "he", "she", "they", or generic terms like "the country", "the city". Replace them always with the exact entity name.

            You must output EXACTLY in this JSON format:
            {
              "triplets": [
                ["EXACT_ENTITY_NAME", "relation", "object"],
                ["EXACT_ENTITY_NAME", "relation", "object"]
              ]
            }
            Do not add any conversational text, greetings, or notes."""
        }

    def _clean_input_text(self, text):
        """Limpia basura común de extracciones HTML/Scraping"""
        text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _chunk_text(self, text, max_chars=800):
        """
        Fragmentador inteligente. Divide el texto por frases (puntos)
        para no cortar ideas a la mitad, agrupándolas en bloques de tamaño máximo.
        """
        # Separamos el texto usando puntos, signos de exclamación o interrogación seguidos de espacio
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # Si añadir la frase supera el límite, guardamos el chunk actual y empezamos uno nuevo
            if len(current_chunk) + len(sentence) < max_chars:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence

        # Añadimos el último fragmento si quedó algo
        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def __extract_triples__(self, text, term):
        # Configuramos los mensajes inyectando las instrucciones estrictas de sujeto
        messages = [
            self.system_prompt,
            {
                "role": "user",
                "content": f"Extract triplets where the subject is EXACTLY '{term}' from this text:\n{text}"
            }
        ]

        try:
            # Forzamos formato JSON a nivel de motor de Ollama
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                format='json'
            )

            raw_content = response['message']['content']
            data = json.loads(raw_content)

            # Post-procesamiento de seguridad: Si el modelo por error usó minúsculas
            # o se equivocó en el sujeto, lo sobreescribimos a la fuerza para proteger tu Ontología.
            triplets_limpios = []
            for t in data.get("triplets", []):
                if len(t) == 3:
                    # Forzamos que la primera posición sea el término exacto
                    triplets_limpios.append([term, t[1], t[2]])

            return triplets_limpios

        except Exception as e:
            print(f"Error procesando fragmento para el término '{term}': {e}")
            return []

    def transform(self, text, term):
        text_limpio = self._clean_input_text(text)

        # NUEVA LÓGICA: Fragmentación por tamaño de caracteres y coherencia de frases
        fragments = self._chunk_text(text_limpio, max_chars=800)
        all_results = []

        for f in fragments:
            triples = self.__extract_triples__(f, term)
            all_results.extend(triples)

        return all_results

