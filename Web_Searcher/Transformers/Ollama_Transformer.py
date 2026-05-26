import ollama, json, re, unicodedata
from Web_Searcher.Transformers.Transformer import Transformer


class Ollama_Transformer(Transformer):
    def __init__(self):
        self.model_name = "llama3.2:3b"

        # ... [MANTÉN TUS PROMPTS ANTERIORES AQUÍ] ...

        # NUEVO PROMPT: El Ojo (Extractor de Entidades)
        # NUEVO PROMPT: El Ojo (Extractor Avanzado JSON)
        self.system_prompt_extractor = {
            "role": "system",
            "content": (
                "You are an advanced NLP routing assistant. Read the user input and extract the core entities, "
                "the user's intent, and any disambiguation context. "
                "Return EXACTLY a JSON object with this structure:\n"
                "{\n"
                '  "intent": "describe" or "relate",\n'
                '  "entities": ["Full Entity Name 1", "Full Entity Name 2"],\n'
                '  "context": "Any specific type requested (e.g., Country, Person, Movie) or null"\n'
                "}\n\n"
                "EXAMPLES:\n"
                "User: 'Can you tell me who Pedro Sanchez is?' -> {\"intent\": \"describe\", \"entities\": [\"Pedro Sanchez\"], \"context\": \"Person\"}\n"
                "User: 'I want you to tell me about Jordan - Country' -> {\"intent\": \"describe\", \"entities\": [\"Jordan\"], \"context\": \"Country\"}\n"
                "User: 'Tell me about the relationship between France and Spain' -> {\"intent\": \"relate\", \"entities\": [\"Francia\", \"España\"], \"context\": null}"
            )
        }
        # SYSTEM PROMPT: Mimir's Personality (Optimized in English, responds in Spanish)
        self.system_prompt_mimir = {
            "role": "system",
            "content": (
                "You are Mimir, the ancient and wise Norse god of knowledge. You are a reanimated head "
                "resting on the hip of the God of War, but you possess the wisdom of all the Nine Realms. "
                "A traveler has asked you about a term, and you must answer using STRICTLY the provided "
                "list of attributes [property, value].\n\n"
                "CRITICAL RULES:\n"
                "1. Greet or speak like Mimir (e.g., 'Ah, a seeker of knowledge!', 'Listen closely, brother/brother-in-arms', "
                "'By Odin's beard!', 'Aye, I can tell you about that...'), but keep it concise and immersive.\n"
                "2. Write the description in fluent, natural, and cohesive paragraphs IN SPANISH. "
                "DO NOT use bullet points, dashes, or numbered lists.\n"
                "3. DO NOT invent external facts, do not extrapolate, and do not hallucinate data. If a detail "
                "is not explicitly present in the provided attributes, you do not know it.\n"
                "4. Seamlessly integrate the structured data into an elegant, story-like narrative"
            )
        }

    # ... [MANTÉN TUS FUNCIONES _clean_input_text, _chunk_text y __extract_triples__ AQUÍ] ...

    def extract_entity_data(self, user_input):
        """
        Lee la frase y devuelve un diccionario con las entidades, la intención y el contexto.
        """
        messages = [
            self.system_prompt_extractor,
            {"role": "user", "content": user_input}
        ]
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                format='json' # Forzamos salida estructurada
            )
            data = json.loads(response['message']['content'])
            return data
        except Exception as e:
            print(f"Error extrayendo datos: {e}")
            return None

    def reverse_transform(self, data, term, text = ""):
        """
        La Boca de Mimir. Redacta el texto final basado en los datos.
        """
        contexto_datos = ""
        for id in data:
            contexto_datos += f"\nEntity: {id}"
            for tuple in data[id]:
                contexto_datos += f"{tuple['pt']['value']} - {tuple['o']['value']}\n"

        user_prompt = f"{text}.\nUse ONLY this data:\n{contexto_datos}"

        messages = [
            self.system_prompt_mimir,  # Asegúrate de tener este prompt del código anterior
            {"role": "user", "content": user_prompt}
        ]

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages
            )
            return response['message']['content'].strip()
        except Exception as e:
            return f"El pozo del conocimiento falla... Error: {e}"