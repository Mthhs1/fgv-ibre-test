import json
from datetime import datetime
import re
from bs4 import BeautifulSoup
import pathlib

log_path = pathlib.Path('./logs')
if not log_path.exists():
    log_path.mkdir()

log_file = "./logs/process_log.txt"

date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")

def log(message:str,file,print_log:bool=False):
    with open(file+date_now, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()}: {message}\n")
    if print_log:
        print(f"{datetime.now()}: {message}")
        

# Função principal, lida com leitura do arquivo, limpeza e escrita do arquivo final
def main():
    
    ### Verificar se o arquivo de notícias limpas já existe, para evitar processamento desnecessário
    result_path_file = pathlib.Path('./dados/noticias_limpas.json')
    if result_path_file.exists():
        log("Arquivo de notícias limpas já existe.", log_file, True)
        return

    print("\n"*3)
    log("Lendo arquivo de notícias brutas", log_file, True)
    
    with open("./dados/noticias_brutas.json", "r", encoding="utf-8") as f:
        noticias_brutas = json.load(f)
    ###
    
    noticias_validas = []
    
    ### Local onde efetivamente as notícias são processadas, chamando a função de limpeza
    for noticia in noticias_brutas:
        log(f"----Processando notícia: {noticia['id']}----", log_file)
        
        dirty_text = noticia['texto']
        cleaned_text = clean_text(dirty_text,noticia['data'],noticia['fonte'])

        if len(cleaned_text) > 20:
            noticia['texto'] = cleaned_text
            noticias_validas.append(noticia)
            
        log(f"----Notícia processada: {noticia['id']}----\n\n\n", log_file)
    ###
    
    ### Escreve o arquivo final de notícias limpas
    log("Escrevendo arquivo de notícias limpas\n\n\n", log_file,True)
    with open("./dados/noticias_limpas.json", "w", encoding="utf-8") as f:
        json.dump(noticias_validas, f, ensure_ascii=False, indent=4)



# Função para limpar mais de um espaço e quebras de linha
def clean_more_one_space_and_breaklines(dirty_text:str):
    cleaned_text = ' '.join(dirty_text.split()).strip()
    difference = get_str_difference(dirty_text, cleaned_text)
    
    
    log("# Limpando mais de um espaço e quebras de linha dos textos", log_file)
    log(f"### Mais de um espaço e quebras de linha removidos: {difference} caracteres", log_file)
    return cleaned_text



# Função para limpar tags HTML usando BeautifulSoup
def clean_html_tags(dirty_text:str):
    soup = BeautifulSoup(dirty_text, "html.parser")
    cleaned_text = soup.get_text()
    difference = get_str_difference(dirty_text, cleaned_text)
    
    
    log("# Limpando tags HTML dos textos", log_file)
    log(f"### Tags HTML removidas: {difference} caracteres", log_file)
    return cleaned_text



# Função para limpar uma palavra específica do texto
def clean_per_word(dirty_text:str, word:str):    
    cleaned_text = dirty_text.replace(word, '')
    difference = get_str_difference(dirty_text, cleaned_text)
    
    
    log(f"# Limpando palavras dos textos: {word}", log_file)
    log(f"### Palavras removidas: {difference} caracteres", log_file)
    return cleaned_text




# Função para limpar a data do texto, formatando a data no objeto no formato YYYY-MM-DD
# para o formato esperado brasileiro DD/MM/YYYY que irá conter no texto
def clean_per_date(dirty_text:str, date:str):
    date = datetime.strptime(date, "%Y-%m-%d")
    date = date.strftime("%d/%m/%Y")
    cleaned_text = dirty_text.replace(date, '')
    difference = get_str_difference(dirty_text, cleaned_text)
    
    
    log(f"# Limpando data dos textos: {date}", log_file)
    log(f"### Datas removidas: {difference} caracteres", log_file)
    return cleaned_text



# Função para limpar horas do texto, usando regex para encontrar padrões de horas
def clean_per_hour(dirty_text:str):
    hour_pattern = r'(?i)(às\s*)?([0-1]?[0-9]|2[0-3])h[0-5][0-9]'
    cleaned_text = re.sub(hour_pattern, '', dirty_text)
    difference = get_str_difference(dirty_text, cleaned_text)
    
    
    log(f"# Limpando horas dos textos", log_file)
    log(f"### Horas removidas: {difference} caracteres", log_file)
    return cleaned_text



# Função para limpar caracteres especiais específicos do texto, como '-', '|', '—'
def clear_per_special_characters(dirty_text:str,char:str):
    cleaned_text = dirty_text.replace(f' {char} ', ' ')
    difference = get_str_difference(dirty_text, cleaned_text)
    
    
    log(f"# Limpando caracteres especiais dos textos: {char}", log_file)
    log(f"### Caracteres '{char}' removidos: {difference} caracteres", log_file)
    return cleaned_text


# Função que retire a fonte do início do texto, caso ela esteja presente
def clear_source_on_start(dirty_text: str,source:str):
    
    index = dirty_text.find(source)
    if index == 0:
        cleaned_text = dirty_text[len(source):].strip()
        difference = get_str_difference(dirty_text, cleaned_text)
        
        log(f"# Limpando fonte no início dos textos: {source}", log_file)
        log(f"### Fontes removidas: {difference} caracteres", log_file)
        return cleaned_text
    return dirty_text

# Função para limpar o texto, chamando as funções de limpeza em sequência
def clean_text(dirty_text:str,date_to_clear:str,source:str):
    processing_text = clean_html_tags(dirty_text)
    processing_text = clean_per_word(processing_text, "Publicado em: ")
    processing_text = clean_per_date(processing_text, date_to_clear)
    processing_text = clean_per_hour(processing_text)
    processing_text = clear_per_special_characters(processing_text, '-')
    processing_text = clear_per_special_characters(processing_text, '|')
    processing_text = clear_per_special_characters(processing_text, '—')
    processing_text = clean_more_one_space_and_breaklines(processing_text)
    cleaned_text = clear_source_on_start(processing_text, source)
    return cleaned_text

def get_str_difference(str1:str, str2:str):
    return len(str1) - len(str2)

if __name__ == "__main__":
    main()
    
