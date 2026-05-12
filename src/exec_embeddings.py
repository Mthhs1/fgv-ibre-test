import json
from sentence_transformers import SentenceTransformer
import torch


def main():
    embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
    
    with open("./dados/noticias_limpa.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    corpus_texts: list[str] = []
    
    for list_item in data:
        title: str = list_item['titulo']
        text:str = list_item['texto']
        unified_text = f"{title}. {text}"
        corpus_texts.append(unified_text.lower())
        
    corpus_embeddings = embedder.encode(corpus_texts, convert_to_tensor=True)
    
    queries = ["mudanças na taxa de juros",
    "mercado de trabalho e desemprego",
    "inflação e preços ao consumidor",]
    
    top_k = min(5, len(corpus_texts))
    
    # Etapa 3: Motor de Busca Semântica
    for query in queries:
        query_embedding = embedder.encode(query, convert_to_tensor=True)
        
        similarity_scores = embedder.similarity(query_embedding, corpus_embeddings)[0]
        scores, indices = torch.topk(similarity_scores, k=top_k)
        
        print("\nQuery:", query)
        print("\nTop 5 notícias mais similares:")

        for score, idx in zip(scores, indices):
            finded_new = data[idx]
            print(f"  - (Score: {score:.4f}) Título: {finded_new['titulo']}")
            
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()