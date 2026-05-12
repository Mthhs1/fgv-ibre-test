import json
import argparse

def main(mode, model, top=5, diff=False):
    
    with open("./results/result.json", "r", encoding="utf-8") as f:
        results = json.load(f)
        
    map_model_name = {
        "mpnet": "paraphrase-multilingual-mpnet-base-v2",
        "minilm": "paraphrase-multilingual-MiniLM-L12-v2",}
    
    model = map_model_name.get(model, model)
    
    for query in results.keys():
        print(f"\n--- Query: '{query}' ---")
        for model_name in results[query].keys():
            
            if model == 'ambos' or model == model_name:
                for title_mode in results[query][model_name].keys():
                    
                    if mode == 'ambos' or mode == title_mode:
                        print(f"\nResultados usando {model_name} - {title_mode}:")
                        ids = results[query][model_name][title_mode]["id"][:top]
                        scores = results[query][model_name][title_mode]["score"][:top]
                        for id, score in zip(ids, scores):
                            print(f"Score: {score:.4f} - Notícia ID: {id}, Título: {get_title_by_id(id)}")
                            
                if diff and mode == 'ambos':
                    ids_sem_titulo = results[query][model_name]["sem_titulo"]["id"][:top]
                    ids_com_titulo = results[query][model_name]["com_titulo"]["id"][:top]
                    
                    difference = get_array_difference(ids_sem_titulo, ids_com_titulo) + get_array_difference(ids_com_titulo, ids_sem_titulo)
                    print(f"\nDiferença entre os resultados com e sem título: {difference}")
    
    return

def get_title_by_id(id):
    with open("./dados/noticias_limpa.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for item in data:
        if item['id'] == id:
            return item['titulo']
    return "Título não encontrado"

def get_array_difference(arr1:list, arr2:list):
    return list(set(arr1) - set(arr2))

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, choices=['com_titulo', 'sem_titulo', 'ambos'], default='ambos', help='Modo de execução: com título, sem título ou ambos')
    parser.add_argument('--model', type=str, choices=['mpnet', 'minilm','ambos'], default='ambos', help='Modelo de embedding a ser utilizado: mpnet, minilm ou ambos')
    parser.add_argument('--top_k', type=int, default=5, help='Número de notícias mais relevantes a serem retornadas para cada consulta')
    parser.add_argument('--diff', action='store_true', help='Exibir diferença entre os resultados com e sem título')

    args = parser.parse_args()
    
    main(args.mode, args.model, args.top_k, args.diff)