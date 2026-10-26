import ollama, json, re, unicodedata
from Web_Searcher.Text_Transformers.Transformer import Transformer


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

        # NUEVO PROMPT: Extractor de relaciones y propiedades semánticas
        self.system_prompt_triples = {
            "role": "system",
            "content": (
                "You are an expert knowledge graph extraction agent. Your job is to extract factual "
                "attributes and semantic relationships from the provided text and output them in a STRICT JSON format.\n\n"
                "CRITICAL RULES:\n"
                "1. For each key fact found, extract the property name (use camelCase, e.g., 'birthDate', 'occupation', 'nationality', 'description') "
                "and its corresponding text value.\n"
                "2. Do not invent properties outside of the text context.\n"
                "3. Output MUST be a valid JSON list of objects, where each object has 'property' and 'value'.\n\n"
                "EXAMPLE OUTPUT:\n"
                "[\n"
                "  {\"property\": \"name\", \"value\": \"Alan Turing\"},\n"
                "  {\"property\": \"birthDate\", \"value\": \"1912-06-23\"},\n"
                "  {\"property\": \"occupation\", \"value\": \"Mathematician and Logician\"}\n"
                "]"
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

    def _clean_input_text(self, text):
        """
        Limpia el texto bruto obtenido del raspado web eliminando saltos de línea duplicados,
        caracteres especiales residuales y espaciados innecesarios para ahorrar tokens.
        """
        if not text:
            return ""
        # Normalizar caracteres unicode, remover etiquetas o metadatos y excesos de espacios
        text = re.sub(r'<[^>]+>', '', text)  # Eliminar remanentes HTML si los hay
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _chunk_text(self, text, max_chars=3000):
        """
        Divide un texto extenso en fragmentos más pequeños (chunks) para asegurar
        que no se desborde la ventana de contexto de Ollama (Llama 3.2).
        """
        cleaned = self._clean_input_text(text)
        # Dividimos de forma segura por oraciones aproximadas o cortes de caracteres
        chunks = []
        for i in range(0, len(cleaned), max_chars):
            chunks.append(cleaned[i:i + max_chars])
        return chunks

    def transform(self, raw_text, term):
        """
        Procesa un bloque de texto completo, lo limpia, lo fragmenta y utiliza
        Ollama para extraer todas las tuplas/propiedades semánticas posibles en formato lista.
        """
        text_chunks = self._chunk_text(raw_text)
        all_extracted_tuples = []

        for chunk in text_chunks:
            if len(chunk) < 50:  # Ignorar fragmentos irrelevantes o muy cortos
                continue

            messages = [
                self.system_prompt_triples,
                {"role": "user", "content": f"Extract properties from this text chunk:\n{chunk} for this term '{term}'"}
            ]

            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    format='json'  # Forzamos al motor a responder bajo una estructura JSON estricta
                )

                # Deserializar la respuesta del fragmento
                chunk_data = json.loads(response['message']['content'])['properties']

                # Validamos que sea una lista antes de extender los resultados globales
                if isinstance(chunk_data, list):
                    for item in chunk_data:
                        try:
                            all_extracted_tuples.append([term, str(item['property']).strip(), str(item['value']).strip()])
                        except Exception as e:
                            print(e)

            except json.JSONDecodeError:
                print("⚠️ Error al decodificar el JSON de un fragmento. Saltando chunk.")
                continue
            except Exception as e:
                print(f"❌ Error en la llamada de extracción con Ollama: {e}")
                continue

        # Eliminar tuplas duplicadas idénticas para optimizar la carga en GraphDB

        return all_extracted_tuples