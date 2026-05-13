import spacy, re, torch
from Web_Searcher.Transformers.Transformer import Transformer
from transformers import pipeline

class Text_Transformer(Transformer):

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def normalize(self, s):
        return re.sub(r"\s+", " ", s.strip())

    def __extract_triples__(self, text):
        doc = self.nlp(text)
        triples = []
        for token in doc:
            if token.lemma_ == "be":
                subj = None; attr = None
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subj = " ".join([t.text for t in child.subtree])
                    if child.dep_ in ("attr", "acomp"):
                        attr = " ".join([t.text for t in child.subtree])
                if subj and attr:
                    triples.append([self.normalize(subj), "is", self.normalize(attr)])
            if token.pos_ == "VERB":
                subj = None; obj = None
                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subj = " ".join([t.text for t in child.subtree])
                    if child.dep_ in ("dobj", "obj"):
                        obj = " ".join([t.text for t in child.subtree])
                if subj and obj:
                    triples.append([self.normalize(subj), token.lemma_, self.normalize(obj)])
        return triples

    def transform(self, text, term):
        tuples = self.__extract_triples__(text)
        for i in range(len(tuples)):
            if term in tuples[i][0]:
                tuples[i][0] = term
            if term in tuples[i][2]:
                tuples[i][2] = term
        return tuples