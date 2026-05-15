import pandas as pd
from datetime import datetime
import re
from bs4 import BeautifulSoup
import pathlib

# Configurações de logging
log_path = pathlib.Path('./logs')
log_path.mkdir(exist_ok=True) # Cria se não existir

date_now = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
log_file = f"./logs/process_log_{date_now}.txt"

def log(message:str, file:str=log_file, print_log:bool=False):
    with open(file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}\n")
    if print_log:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {message}")

# Função para calcular a diferença de caracteres entre o texto antes e depois da limpeza
def get_str_difference(df_before: pd.Series, df_after: pd.Series) -> int:
    return int(df_before.str.len().sum() - df_after.str.len().sum())

# Função para limpar o texto de uma notícia, aplicando as regras definidas
def clean_html_tags(dirty_text: str):
    return BeautifulSoup(dirty_text, "html.parser").get_text()

# Função para extrair a data do texto e removê-la
def clean_per_date(row: pd.Series):
    dirty_text = row["texto"]
    try:
        date_obj = datetime.strptime(row["data"], "%Y-%m-%d")
        date_str = date_obj.strftime("%d/%m/%Y")
        return dirty_text.replace(date_str, '')
    except Exception:
        return dirty_text
    
# Função para extrair a fonte do inicio do texto e removê-la
def clear_source_on_start(row: pd.Series):
    source = row["fonte"]
    dirty_text = row["texto"]
    
    if dirty_text.startswith(source):
        return dirty_text[len(source):].strip()
    return dirty_text

# Função principal de limpeza
def clean_text(df: pd.DataFrame) -> pd.DataFrame:
    
    # --- 1. Remover HTML ---
    text_before = df["texto"].copy()
    df["texto"] = df["texto"].apply(clean_html_tags)
    log(f"Tags HTML removidas. Caracteres limpos: {get_str_difference(text_before, df['texto'])}")
    
    # --- 2. Remover palavra específica --
    text_before = df["texto"].copy()
    df["texto"] = df["texto"].str.replace("Publicado em: ", "", regex=False)
    log(f"Palavras 'Publicado em: ' removidas. Caracteres limpos: {get_str_difference(text_before, df['texto'])}")
    
    # --- 3. Remover Datas ---
    text_before = df["texto"].copy()
    df["texto"] = df.apply(clean_per_date, axis="columns")
    log(f"Datas extraídas do texto. Caracteres limpos: {get_str_difference(text_before, df['texto'])}")
    
    # --- 4. Remover Horas ---
    text_before = df["texto"].copy()
    hour_pattern = r'(?i)(às\s*)?([0-1]?[0-9]|2[0-3])h[0-5][0-9]'
    df["texto"] = df["texto"].str.replace(hour_pattern, '', regex=True)
    log(f"Horas removidas. Caracteres limpos: {get_str_difference(text_before, df['texto'])}")
    
    # --- 5. Remover Caracteres Especiais ---
    text_before = df["texto"].copy()
    # Pega espaços ao redor de traços, pipes e travessões e transforma em um único espaço
    df["texto"] = df["texto"].str.replace(r' [-|—] ', ' ', regex=True)
    log(f"Caracteres especiais (-, |, —) removidos. Caracteres limpos: {get_str_difference(text_before, df['texto'])}")
    
    # --- 6. Remover Múltiplos Espaços e Quebras de Linha ---
    text_before = df["texto"].copy()
    df["texto"] = df["texto"].str.replace(r'\s+', ' ', regex=True).str.strip()
    log(f"Espaços extras removidos. Caracteres limpos: {get_str_difference(text_before, df['texto'])}")
    
    # --- 7. Remover Fonte no Início ---
    text_before = df["texto"].copy()
    df["texto"] = df.apply(clear_source_on_start, axis="columns")
    log(f"Fontes no início removidas. Caracteres limpos: {get_str_difference(text_before, df['texto'])}")
    
    return df

def main():
    log("Lendo arquivo de notícias brutas", print_log=True)
    
    # Lê os dados apenas usando o Pandas
    df = pd.read_json("./dados/noticias_brutas.json", convert_dates=False)
    df = df.set_index('id')
        
    df_cleaned = clean_text(df)
    
    # Filtrar textos maiores que 20 caracteres
    df_cleaned = df_cleaned[df_cleaned["texto"].str.len() > 20]
    
    log(f"Salvando {len(df_cleaned)} registros finais em noticias_limpas.json", print_log=True)
    df_cleaned.reset_index().to_json("./dados/noticias_limpas.json", orient="records", force_ascii=False, indent=2)

if __name__ == "__main__":
    main()