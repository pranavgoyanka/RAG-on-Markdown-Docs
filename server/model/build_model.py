import re
import chromadb
from chromadb.config import Settings
import pprint
import numpy as np
import pandas as pd
import markdown_to_json
import logging

# from server.model.utils import clean_markdown, extract_keywords_tfidf
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import re
from sklearn.feature_extraction.text import TfidfVectorizer


class rag:

    def __init__(self, file_path, db_dir):
        self.db_dir = db_dir
        self.file_path = file_path
        self.collection_name = "rag_db"
        self.load_data()
        self.prepare_database()
        self.load_llm()
        self.initilised = True
        logging.info("rag init complete!")

    def isInitialised(self):
        return self.initilised

    def load_data(self):
        logging.info("Loading dataset...")
        with open(self.file_path, "r") as file:
            data = file.read()

        md_dict = markdown_to_json.dictify(data)

        # dfs into the dictionary
        def dfs_dict(d, path):
            if path is None:
                path = []

            for key, value in d.items():
                # path.append({"key": key, "value": str(value)})

                if isinstance(value, dict):
                    # recursively apply dfs if the value is another dictionary
                    dfs_dict(value, path)
                else:
                    # reached the end
                    # cleanup the value and key

                    path.append({"key": key, "value": str(value)})

        all_md_keys_dict = []
        dfs_dict(md_dict, all_md_keys_dict)
        # create a dataframe out of all of the doc
        md_df = pd.DataFrame.from_dict(all_md_keys_dict)
        md_df["id"] = md_df.index
        md_df["key"] = md_df["key"].apply(clean_markdown)
        md_df["value"] = md_df["value"].apply(clean_markdown)
        self.md_df = md_df

    # TODO: fix for clean_db = False
    def prepare_database(self, clean_db=True):
        logging.info("Preparing Chroma Client...")

        self.chroma_client = chromadb.PersistentClient(path=self.db_dir)

        # delete the collection if it already exists
        if clean_db:
            if len(
                self.chroma_client.list_collections()
            ) > 0 and self.collection_name in [
                self.chroma_client.list_collections()[0].name
            ]:
                self.chroma_client.delete_collection(name=self.collection_name)
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name
            )

        # some constants
        DOCUMENT = "value"
        TOPIC = "key"

        # populate the collection
        self.collection.add(
            documents=self.md_df[DOCUMENT].tolist(),
            metadatas=[{TOPIC: topic} for topic in self.md_df[TOPIC].tolist()],
            ids=[f"id{x}" for x in range(len(self.md_df))],
        )

    def load_llm(self):
        logging.info("Loading LLM...")
        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        lm_model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True)

        self.pipe = pipeline(
            "text-generation",
            model=lm_model,
            tokenizer=tokenizer,
            max_new_tokens=256,
            device_map="auto",
        )

    def get_context_from_db(self, keywords, results_to_use=1):
        ctxs = []
        for keyword in keywords:
            ctxs.append(
                self.collection.query(query_texts=[keyword], n_results=results_to_use)
            )
        context = ""
        for ctx in ctxs:
            temp = " ".join([f"#{str(i)}" for i in ctx["documents"][0]])
            context = context + " " + temp
        return context

    def generate_extended_prompt(
        self, question, context_to_lookup=None, results_to_use=1
    ):
        context = ""
        # lookup the vector database for semantically similar data
        if context_to_lookup:
            context = self.get_context_from_db(context_to_lookup, results_to_use)

        # populate the prompt template
        prompt_template = f"""
        Relevant context: {context}
        Considering the above context, answer the following question.
        Question: {question}
        """
        
        ctxLen = len( f"""
        Relevant context: {context}
        Considering the above context, answer the following question.""")
        
        return prompt_template, ctxLen

    def get_llm_response(self, question, results_to_use=3, enableRAG=True):
        ctx_lookup = ""
        if enableRAG:
            ctx_lookup = extract_keywords_tfidf(question)
        ext_prompt, ctxLen = self.generate_extended_prompt(question, ctx_lookup, results_to_use)
        logging.info("Running user query with (enableRAG = " + str(enableRAG) + ")...")
        lm_response = self.pipe(ext_prompt)
        return lm_response[0]["generated_text"][ctxLen : ]


def clean_markdown(line):
    # Remove headers (e.g., # Header, ## Header)
    line = re.sub(r"^#+\s", "", line)
    # Remove bold and italics (e.g., **bold**, *italic*)
    line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
    line = re.sub(r"\*(.*?)\*", r"\1", line)
    # Remove inline code (e.g., `code`)
    line = re.sub(r"`(.*?)`", r"\1", line)
    # Remove links (e.g., [text](url))
    line = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", line)
    # Remove images (e.g., ![alt text](url))
    line = re.sub(r"!\[(.*?)\]\((.*?)\)", r"\1", line)
    # Remove blockquotes (e.g., > Quote)
    line = re.sub(r"^>\s", "", line)
    # Remove unordered list items (e.g., - Item, * Item)
    line = re.sub(r"^[-*]\s", "", line)
    # Remove ordered list items (e.g., 1. Item)
    line = re.sub(r"^\d+\.\s", "", line)
    # Remove horizontal rules (e.g., ---)
    line = re.sub(r"^-{3,}$", "", line)
    # Remove other markdown artifacts as needed
    return line.strip()


def extract_keywords_tfidf(text, num_keywords=5):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]
    keywords = sorted(
        list(zip(feature_names, tfidf_scores)), key=lambda x: x[1], reverse=True
    )
    return [word for word, score in keywords[:num_keywords]]
