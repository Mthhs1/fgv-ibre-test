import json
from sentence_transformers import SentenceTransformer
import torch
import pathlib

queries = ["mudanças na taxa de juros",
    "mercado de trabalho e desemprego",
    "inflação e preços ao consumidor",]

embedders_names = [
    "paraphrase-multilingual-mpnet-base-v2",
    "paraphrase-multilingual-MiniLM-L12-v2"
]

# Cria um dicionário vazio para armazenar os resultados
# query: { model: { corpus_texts: {id: int, score: float} } }
def create_empty_res_dict(queries:list[str], embedders_names:list[str]):
    
    res = {}
    for query in queries:
        res[query] = {}
        for name in embedders_names:
            res[query][name] = {
                "sem_titulo": {"id": [], "score": []},
                "com_titulo": {"id": [], "score": []}
            }
    return res

def get_corpus_texts(data:list[dict]):
    
    corpus_texts: list[str] = []
    corpus_texts_with_title: list[str] = []
    
    for list_item in data:
        title: str = list_item['titulo']
        text:str = list_item['texto']
        unified_text = f"Título: {title}. Contexto: {text}"
        
        corpus_texts.append(text.lower())
        corpus_texts_with_title.append(unified_text.lower())
        
    return corpus_texts, corpus_texts_with_title

# Calcula os scores de similaridade entre a consulta e o corpus, retornando os top_k resultados 
def get_scores(model, query_embedding, corpus_embeddings, top_k:int=5):
    
    similarity_scores = model.similarity(query_embedding, corpus_embeddings)[0]
    scores, indices = torch.topk(similarity_scores, k=top_k)
    
    return scores, indices

def main():
    
    embedders = [
        SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2'),
        SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    ]
    
    cleaned_data_path = pathlib.Path('./dados/noticias_limpas.json')
    if not cleaned_data_path.exists():
        print("Arquivo de notícias limpas não encontrado. Por favor, execute o script de limpeza de dados primeiro.")
        return
    
    with open("./dados/noticias_limpas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    res = create_empty_res_dict(queries, embedders_names)
    corpus_texts, corpus_texts_with_title = get_corpus_texts(data)
        
    # Itera sobre cada modelo de embedding e cada consulta, calculando os scores e armazenando os resultados 
    for embedder, name in zip(embedders, embedders_names):
        
        corpus_embeddings = embedder.encode(corpus_texts, convert_to_tensor=True)
        corpus_embeddings_with_title = embedder.encode(corpus_texts_with_title, convert_to_tensor=True)
        
        for query in queries:
            
            query_embedding = embedder.encode(query, convert_to_tensor=True)
            scores, indices = get_scores(embedder, query_embedding, corpus_embeddings, top_k=len(corpus_embeddings))
            scores_with_title, indices_with_title = get_scores(embedder, query_embedding, corpus_embeddings_with_title, top_k=len(corpus_embeddings_with_title))

            #Pra cada score e índice retornados, armazena o ID da notícia e o score no dicionário de resultados
            for score, index in zip(scores, indices):
                res[query][name]["sem_titulo"]["id"].append(data[index]['id'])
                res[query][name]["sem_titulo"]["score"].append(score.data.item())
            
            for score, index in zip(scores_with_title, indices_with_title):
                res[query][name]["com_titulo"]["id"].append(data[index]['id'])
                res[query][name]["com_titulo"]["score"].append(score.data.item())
    
    path = pathlib.Path('./results')
    if not path.exists():
        path.mkdir()
    
    with open("./results/result.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=5)

if __name__ == "__main__":
    main()