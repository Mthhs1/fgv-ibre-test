import json
from datetime import datetime
import re
from bs4 import BeautifulSoup

log_path = "./logs/process_log.txt"
date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

def log(message:str,file,print_log:bool=False):
    with open(file+date_now, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()}: {message}\n")
    if print_log:
        print(f"{datetime.now()}: {message}")
        

# Função principal, lida com leitura do arquivo, limpeza e escrita do arquivo final
def main():
    
    log("\n\n\nLendo arquivo de notícias brutas", log_path,True)
    with open("./dados/noticias_brutas.json", "r", encoding="utf-8") as f:
        noticias_brutas = json.load(f)
        
    noticias_validas = []
    
    for noticia in noticias_brutas:
        log(f"----Processando notícia: {noticia['id']}----", log_path)
        dirty_text = noticia['texto']
        cleaned_text = clean_text(dirty_text,noticia['data'])

        if len(cleaned_text) > 20:
            noticia['texto'] = cleaned_text
            noticias_validas.append(noticia)
            
    log("Escrevendo arquivo de notícias limpas\n\n\n", log_path,True)
    with open("./dados/noticias_limpa.json", "w", encoding="utf-8") as f:
        json.dump(noticias_validas, f, ensure_ascii=False, indent=4)

# Função para limpar mais de um espaço e quebras de linha
# ' ' & '\n'
def clean_more_one_space_and_breaklines(dirty_text:str):
    cleaned_text = ' '.join(dirty_text.split())
    return cleaned_text

# Função para limpar tags HTML usando BeautifulSoup
# O método get_text() extrai o texto, removendo as tags HTML
def clean_html_tags(dirty_text:str):
    log("Limpando tags HTML dos textos", log_path)
    soup = BeautifulSoup(dirty_text, "html.parser")
    cleaned_text = soup.get_text()
    return cleaned_text

# Função para limpar uma palavra específica do texto
def clean_per_word(dirty_text:str, word:str):    
    log(f"Limpando palavras dos textos: {word}", log_path)
    cleaned_text = dirty_text.replace(word, '')
    return cleaned_text

# Função para limpar a data do texto, formatando a data no objeto no formato YYYY-MM-DD
# para o formato esperado brasileiro DD/MM/YYYY e removendo do texto
def clean_per_date(dirty_text:str, date:str):
    date = datetime.strptime(date, "%Y-%m-%d")
    date = date.strftime("%d/%m/%Y")
    log(f"Limpando data dos textos: {date}", log_path)
    cleaned_text = dirty_text.replace(date, '')
    return cleaned_text

# Função para limpar horas do texto, usando regex para encontrar padrões 
# de horas
def clean_per_hour(dirty_text:str):
    hour_pattern = r'(?i)(às\s*)?([0-1]?[0-9]|2[0-3])h[0-5][0-9]'
    log("Limpando horas dos textos", log_path)
    cleaned_text = re.sub(hour_pattern, '', dirty_text)
    return cleaned_text

# Função para limpar caracteres especiais específicos do texto, como '-', '|', '—'
def clear_per_special_characters(dirty_text:str,char:str):
    log(f"Limpando caracteres especiais dos textos: {char}", log_path)
    cleaned_text = dirty_text.replace(f' {char} ' ,' ')
    return cleaned_text

# Função para limpar o texto, chamando as funções de limpeza em sequência
def clean_text(dirty_text:str,date_to_clear:str):
    cleaned_text = clean_html_tags(dirty_text)
    cleaned_text = clean_per_word(cleaned_text, "Publicado em: ")
    cleaned_text = clean_per_date(cleaned_text, date_to_clear)
    cleaned_text = clean_per_hour(cleaned_text)
    cleaned_text = clear_per_special_characters(cleaned_text, '-')
    cleaned_text = clear_per_special_characters(cleaned_text, '|')
    cleaned_text = clear_per_special_characters(cleaned_text, '—')
    cleaned_text = clean_more_one_space_and_breaklines(cleaned_text)
    return cleaned_text

if __name__ == "__main__":
    main()
    
