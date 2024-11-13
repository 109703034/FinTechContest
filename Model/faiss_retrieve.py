import os
import json
import faiss
import numpy as np
import jieba
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import re
from typing import List, Dict, Tuple
from collections import Counter
import argparse
class ImprovedFAISSRetriever:
    """
    A retriever that utilizes FAISS and Sentence-BERT to perform efficient document retrieval
    based on semantic and keyword matching.
    """

    def __init__(self, model_name='shibing624/text2vec-base-chinese'):
        """
        Initializes the ImprovedFAISSRetriever with a sentence embedding model.

        Args:
            model_name (str): The model name to load with SentenceTransformer.
                Defaults to 'shibing624/text2vec-base-chinese'.
        """
        self.encoder = SentenceTransformer(model_name)
        self.window_size = 3  
        
    def preprocess_text(self, text: str) -> str:
        """
        Preprocesses the input text by removing extra whitespace and non-Chinese characters.

        Args:
            text (str): The text to preprocess.

        Returns:
            str: The cleaned text.
        """
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\u4e00-\u9fff，。！？]', '', text)
        return text
    
    def get_keywords(self, text: str) -> List[str]:
        """
        Extracts keywords from the text using Jieba for tokenization.

        Args:
            text (str): The input text to extract keywords from.

        Returns:
            List[str]: A list of keywords with a minimum length of 2 characters.
        """
        words = jieba.cut(text)
        return [w for w in words if len(w.strip()) > 1]
    
    def split_document(self, text: str) -> List[str]:
        """
        Splits the document into windows of paragraphs for indexing.

        Args:
            text (str): The document text to split.

        Returns:
            List[str]: A list of paragraph windows with minimum length of 50 characters.
        """
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        windows = []
        for i in range(len(paragraphs)):
            window_paragraphs = paragraphs[i:i + self.window_size]
            if window_paragraphs:
                window_text = ' '.join(window_paragraphs)
                window_text = self.preprocess_text(window_text)
                if len(window_text) > 50:  
                    windows.append(window_text)
        return windows
    
    def build_index(self, txt_folders: Dict[str, str], faq_path: str):
        """
        Builds FAISS indices for each document category by encoding and indexing document segments.

        Args:
            txt_folders (Dict[str, str]): A dictionary of category to folder path mappings.
            faq_path (str): The path to the FAQ JSON file.

        Returns:
            None
        """
        # 存儲文檔段落及其對應的嵌入
        self.doc_segments = {
            "finance": {},  # pid -> [segments]
            "insurance": {},
            "faq": {}
        }
        self.embeddings = {
            "finance": [],
            "insurance": [],
            "faq": []
        }
        self.id_mappings = {
            "finance": {},  # embedding_id -> (pid, segment_id)
            "insurance": {},
            "faq": {}
        }
        
        for category, folder_path in txt_folders.items():
            print(f"Processing {category} documents...")
            for filename in tqdm(os.listdir(folder_path)):
                if filename.endswith('.txt'):
                    pid = int(filename.replace('.txt', ''))
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                        segments = self.split_document(text)
                        self.doc_segments[category][pid] = segments
                        
                        for seg_id, segment in enumerate(segments):
                            embedding = self.encoder.encode(segment, convert_to_numpy=True)
                            self.embeddings[category].append(embedding)
                            embed_id = len(self.embeddings[category]) - 1
                            self.id_mappings[category][embed_id] = (pid, seg_id)
        
        print("Processing FAQ documents...")
        with open(faq_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
            for pid, contents in tqdm(faq_data.items()):
                pid = int(pid)
                segments = []
                for content in contents:
                    qa_text = f"{content['question']} {' '.join(content['answers'])}"
                    qa_text = self.preprocess_text(qa_text)
                    segments.append(qa_text)
                
                self.doc_segments["faq"][pid] = segments
                for seg_id, segment in enumerate(segments):
                    embedding = self.encoder.encode(segment, convert_to_numpy=True)
                    self.embeddings["faq"].append(embedding)
                    embed_id = len(self.embeddings["faq"]) - 1
                    self.id_mappings["faq"][embed_id] = (pid, seg_id)
        
        self.indices = {}
        for category in ["finance", "insurance", "faq"]:
            if self.embeddings[category]:
                embeddings = np.array(self.embeddings[category])
                quantizer = faiss.IndexFlatIP(embeddings.shape[1])
                index = faiss.IndexIVFFlat(quantizer, embeddings.shape[1], 
                                         min(100, len(embeddings)), faiss.METRIC_INNER_PRODUCT)
                index.train(embeddings)
                index.add(embeddings)
                self.indices[category] = index
    
    def get_combined_score(self, query_embedding: np.ndarray, doc_embedding: np.ndarray, 
                          query_keywords: List[str], doc_text: str) -> float:
        """
        Computes a combined score based on semantic similarity, keyword overlap, and text length.

        Args:
            query_embedding (np.ndarray): The embedding of the query text.
            doc_embedding (np.ndarray): The embedding of the document text.
            query_keywords (List[str]): A list of keywords from the query.
            doc_text (str): The document text.

        Returns:
            float: The final score combining similarity, keyword match, and length penalty.
        """        
        # 1. 計算語義相似度（使用內積而不是L2距離）
        semantic_score = np.dot(query_embedding, doc_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding))
        
        # 2. 計算關鍵詞匹配得分
        doc_keywords = self.get_keywords(doc_text)
        query_counter = Counter(query_keywords)
        doc_counter = Counter(doc_keywords)
        keyword_overlap = sum((query_counter & doc_counter).values())
        keyword_score = keyword_overlap / (len(query_keywords) + 1e-10)
        
        # 3. 長度懲罰（避免過短的文本）
        length_penalty = min(1.0, len(doc_text) / 200)
        
        final_score = (semantic_score * 0.5 + 
                      keyword_score * 0.4 + 
                      length_penalty * 0.1)
        
        return final_score
    
    def search(self, question_data: Dict) -> int:
        """
        Searches for the best matching document based on the query.

        Args:
            question_data (Dict): A dictionary containing 'query', 'category', and 'source' fields.

        Returns:
            int: The PID of the best matching document.
        """
        query = question_data["query"]
        category = question_data["category"]
        source_pids = question_data["source"]
        
        query = self.preprocess_text(query)
        query_keywords = self.get_keywords(query)
        query_embedding = self.encoder.encode(query, convert_to_numpy=True)
        
        best_score = -float('inf')
        best_pid = source_pids[0] 
        
        candidate_embeddings = []
        candidate_indices = []
        
        for pid in source_pids:
            if pid in self.doc_segments[category]:
                segments = self.doc_segments[category][pid]
                for seg_id, segment in enumerate(segments):
                    embedding_id = None
                    # 找到對應的embedding_id
                    for eid, (p, s) in self.id_mappings[category].items():
                        if p == pid and s == seg_id:
                            embedding_id = eid
                            break
                    if embedding_id is not None:
                        candidate_embeddings.append(self.embeddings[category][embedding_id])
                        candidate_indices.append((pid, seg_id))
        
        if candidate_embeddings:
            candidate_embeddings = np.array(candidate_embeddings)
            temp_index = faiss.IndexFlatIP(candidate_embeddings.shape[1])
            temp_index.add(candidate_embeddings)
            
            D, I = temp_index.search(query_embedding.reshape(1, -1), k=min(5, len(candidate_embeddings)))
            
            for i in range(len(I[0])):
                idx = I[0][i]
                pid, seg_id = candidate_indices[idx]
                segment_text = self.doc_segments[category][pid][seg_id]
                score = self.get_combined_score(query_embedding, 
                                             candidate_embeddings[idx],
                                             query_keywords, 
                                             segment_text)
                if score > best_score:
                    best_score = score
                    best_pid = pid
        
        return best_pid

    def process_questions(self, questions_file: str, output_file: str):
        """
        Processes a list of questions and saves the best matching document IDs to a file.

        Args:
            questions_file (str): Path to the JSON file containing questions.
            output_file (str): Path to the output JSON file to save results.

        Returns:
            None
        """
        with open(questions_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = []
        for question in tqdm(data["questions"], desc="Processing questions"):
            best_pid = self.search(question)
            results.append({
                "qid": question["qid"],
                "retrieve": best_pid
            })
        json_result = {}
        json_result["answers"] = results

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some paths and files.')
    parser.add_argument('--question_path', type=str, required=True, help='讀取發布題目路徑')  
    parser.add_argument('--source_path', type=str, required=True, help='讀取參考資料(txt)路徑') 
    parser.add_argument('--output_path', type=str, required=True, help='輸出符合參賽格式的答案路徑')
    args = parser.parse_args() 

    retriever = ImprovedFAISSRetriever()
    
    txt_folders = {
        "finance": os.path.join(args.source_path, "finance_noBlank"),
        "insurance": os.path.join(args.source_path, "insurance")
    }
    faq_path = os.path.join(args.source_path, "faq/pid_map_content.json")
    
    print("Building index...")
    retriever.build_index(txt_folders, faq_path)
    
    print("Processing questions...")
    retriever.process_questions(
        questions_file = args.question_path,
        output_file = args.output_path
    )

