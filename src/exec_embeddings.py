import json
from sentence_transformers import SentenceTransformer
import torch

queries = ["mudanças na taxa de juros",
    "mercado de trabalho e desemprego",
    "inflação e preços ao consumidor",]

embedders = [
    SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2'),
    SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
]
embedders_names = [
    "paraphrase-multilingual-mpnet-base-v2",
    "paraphrase-multilingual-MiniLM-L12-v2"
]

with open("./dados/noticias_limpa.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    
# Res format
# query: { model: { corpus_texts: {id: int, score: float} } }
def create_empty_res_dict(queries:list[str], embedders_names:list[str]):
    res = {}
    for query in queries:
        res[query] = {}
        for name in embedders_names:
            res[query][name] = {
                "sem título": {"id": [], "score": []},
                "com título": {"id": [], "score": []}
            }
    return res

def main():
    res = create_empty_res_dict(queries, embedders_names)
    corpus_texts, corpus_texts_with_title = get_corpus_texts(data)
        
    for embedder, name in zip(embedders, embedders_names):
        
        corpus_embeddings = embedder.encode(corpus_texts, convert_to_tensor=True)
        corpus_embeddings_with_title = embedder.encode(corpus_texts_with_title, convert_to_tensor=True)
        
        for query in queries:
            
            id_top_news_1 = []
            id_top_news_2 = []
            
            print(f"\n--- Query: '{query}' | Modelo: {name} ---")
            query_embedding = embedder.encode(query, convert_to_tensor=True)
            scores, indices = get_scores(embedder, query_embedding, corpus_embeddings)

            print(f"Resultados usando {name}: (sem título)")
            for score, index in zip(scores, indices):
                print(f"Score: {score:.4f} - Notícia: {data[index]['titulo']}")
                id_top_news_1.append(data[index]['id'])
                res[query][name]["sem título"]["id"].append(data[index]['id'])
                res[query][name]["sem título"]["score"].append(score.data.item())
            
            scores_with_title, indices_with_title = get_scores(embedder, query_embedding, corpus_embeddings_with_title)
            
            print(f"\nResultados usando {name}: (com título)")
            for score, index in zip(scores_with_title, indices_with_title):
                print(f"Score: {score:.4f} - Notícia: {data[index]['titulo']}")
                id_top_news_2.append(data[index]['id'])
                res[query][name]["com título"]["id"].append(data[index]['id'])
                res[query][name]["com título"]["score"].append(score.data.item())
            
            difference = get_array_difference(id_top_news_1, id_top_news_2) + get_array_difference(id_top_news_2, id_top_news_1)
            print(f"Id das notícias melhor ranqueadas sem título: {id_top_news_1}")
            print(f"Id das notícias melhor ranqueadas com título: {id_top_news_2}")
            print(f"Notícias sairam/entraram no rankeamento: {difference}")
    
    with open("./results.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=5)

def get_corpus_texts(data:list[dict]):
    
    corpus_texts: list[str] = []
    corpus_texts_with_title: list[str] = []
    
    for list_item in data:
        title: str = list_item['titulo']
        text:str = list_item['texto']
        unified_text = f"{title}. {text}"
        
        corpus_texts.append(text.lower())
        corpus_texts_with_title.append(unified_text.lower())
        
        
    return corpus_texts, corpus_texts_with_title

    
def get_scores(model, query_embedding, corpus_embeddings, top_k:int=5):
    
    
    similarity_scores = model.similarity(query_embedding, corpus_embeddings)[0]
    scores, indices = torch.topk(similarity_scores, k=top_k)
    
    return scores, indices

def get_array_difference(arr1:list, arr2:list):
    return list(set(arr1) - set(arr2))

if __name__ == "__main__":
    main()