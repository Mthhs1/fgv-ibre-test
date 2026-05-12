import clean_data
import exec_embeddings

def main():
    beautiful_print("Iniciando o processo de limpeza dos dados")
    clean_data.main()
    beautiful_print("Processo de limpeza concluído")
    print("\n\n\n")
    beautiful_print("Iniciando o processo de execução dos embeddings")
    exec_embeddings.main()
    beautiful_print("Processo de execução dos embeddings concluído")
    
def beautiful_print(text:str):
    print("\n" + "="*25 + f' {text} ' + "="*25 + "\n")

main()