import ollama, json, re, unicodedata
from Web_Searcher.Text_Transformers.Transformer import Transformer


class Ollama_Transformer(Transformer):
    def __init__(self):
        self.model_name = "llama3.2:3b"

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

        self.system_prompt_triples = {
            "role": "system",
            "content": (
                "You are an expert knowledge graph extraction agent. Your job is to extract factual "
                "attributes and semantic relationships from the provided text and output them in a STRICT JSON format.\n\n"
                "CRITICAL RULES:\n"
                "1. Extract property names in camelCase (e.g., 'birthDate', 'occupation', 'nationality', 'description') "
                "and their corresponding values.\n"
                "2. Do not invent facts outside of the text context.\n"
                "3. Output MUST be a JSON object containing a 'properties' key with an array of objects.\n\n"
                "EXAMPLE OUTPUT:\n"
                "{\n"
                '  "properties": [\n'
                '    {"property": "name", "value": "Alan Turing"},\n'
                '    {"property": "birthDate", "value": "1912-06-23"},\n'
                '    {"property": "occupation", "value": "Mathematician and Logician"}\n'
                "  ]\n"
                "}"
            )
        }

    def extract_entity_data(self, user_input):
        messages = [
            self.system_prompt_extractor,
            {"role": "user", "content": user_input}
        ]
        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                format='json'
            )
            data = json.loads(response['message']['content'])
            return data
        except Exception as e:
            print(f"Error extrayendo datos: {e}")
            return None

    def reverse_transform(self, data, term, text=""):
        contexto_datos = ""
        for id in data:
            contexto_datos += f"\nEntity: {id}\n"
            for tuple in data[id]:
                contexto_datos += f"{tuple['pt']['value']} - {tuple['o']['value']}\n"

        user_prompt = f"{text}.\nUse ONLY this data:\n{contexto_datos}"

        messages = [
            self.system_prompt_mimir,
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
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[\r\n\t]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def transform(self, raw_text, term):
        """
        Procesa el texto completo de una sola vez (sin fragmentación) utilizando
        la gran ventana de contexto del modelo, extrayendo las tuplas semánticas de forma segura.
        """
        cleaned_text = self._clean_input_text(raw_text)
        if not cleaned_text:
            return []

        messages = [
            self.system_prompt_triples,
            {"role": "user", "content": f"Extract properties from this text for the term '{term}':\n{cleaned_text}"}
        ]

        all_extracted_tuples = []
        seen_tuples = set()

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                format='json'
            )

            content = response['message']['content'].strip()

            # Limpieza de bloques markdown ```json ... ``` si los hubiere
            json_match = re.search(r'\{.*\}|\[.*\]', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            parsed_json = json.loads(content)
            extracted_list = []

            # Deserialización resiliente para adaptarse a la respuesta del modelo
            if isinstance(parsed_json, dict):
                if 'properties' in parsed_json and isinstance(parsed_json['properties'], list):
                    extracted_list = parsed_json['properties']
                elif 'triples' in parsed_json and isinstance(parsed_json['triples'], list):
                    extracted_list = parsed_json['triples']
                else:
                    for k, v in parsed_json.items():
                        if isinstance(v, (str, int, float)):
                            extracted_list.append({"property": k, "value": str(v)})
            elif isinstance(parsed_json, list):
                extracted_list = parsed_json

            # Procesamiento y formateo de las tuplas evitando duplicados
            for item in extracted_list:
                if isinstance(item, dict) and 'property' in item and 'value' in item:
                    p_val = str(item['property']).strip().replace(' ', '')
                    v_val = str(item['value']).strip()

                    if p_val and v_val:
                        tuple_key = (term, p_val, v_val)
                        if tuple_key not in seen_tuples:
                            seen_tuples.add(tuple_key)
                            all_extracted_tuples.append([term, p_val, v_val])

        except json.JSONDecodeError as e:
            print(f"⚠️ Error al decodificar JSON del texto completo: {e}")
        except Exception as e:
            print(f"❌ Error en la llamada con Ollama: {e}")

        return all_extracted_tuples