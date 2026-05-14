# Desafio Técnico — Estágio em Ciência de Dados
**FGV IBRE — Instituto Brasileiro de Economia**

---

## Contexto

O FGV IBRE produz indicadores econômicos de referência para o Brasil — como o IGP-M, o IPC e o ICC — e publica dezenas de notas técnicas por mês. Nesse volume de produção textual, a capacidade de **buscar e recuperar informação relevante** de forma eficiente é cada vez mais valiosa.

Neste desafio, você vai construir um **mini motor de busca semântico** aplicado a notícias econômicas. O objetivo não é implementar um sistema de produção, mas demonstrar que você sabe limpar dados textuais, aplicar modelos de linguagem e raciocinar sobre similaridade semântica.

---

## Visão Geral

O desafio está dividido em **três etapas encadeadas**:

```
noticias_brutas.json  →  [Etapa 1: Limpeza]  →  dados_limpos
                                                         ↓
                                               [Etapa 2: Embeddings]
                                                         ↓
                                               [Etapa 3: Busca Semântica]
```

## Etapa 1: Limpeza de Dados

A primeira etapa é transformar o arquivo `noticias_brutas.json` em um formato mais limpo e estruturado. O meu primeiro passo foi dar uma investigada geral no arquivo  original de dados brutos. A princípio, o arquivo parecia conter uma lista de dicionários e não havia muitas notícias lixos (curto) ou duplicatas. O campo de texto estava com diversos caracteres, tags HTML, metadados e formatações que não eram relevantes para a análise.

O arquivo de limpeza `clean_data.py` recebe o arquivo bruto, processa cada notícia e salva um novo arquivo `noticias_limpa.json` com as seguintes transformações:

- **Remoção de espaços extras e quebras de linha**: `clean_more_one_space_and_breaklines` garante que o texto fique mais uniforme, eliminando múltiplos espaços e quebras de linha desnecessárias.

- **Limpeza de tags HTML**: `clean_html_tags` usa uma função da biblioteca BeautifulSoup para extrair apenas o texto de uma sentença, removendo quaisquer tags HTML presentes.

- **Limpeza de palavras<sup>1</sup>**: `clean_per_words` remove palavras irrelevantes que geralmente estão presentes nos metadados da notícia e que não agregam valor semântico. Após uma verificação manual dos dados, identifiquei palavras como "Publicado em" no início do texto. Essa é função pode acidentalmente remover palavras que sejam parte do texto, mas acredito que a maioria dos casos seja de metadados, para um conjunto de dados maior, seria interessante criar uma função mais robusta para identificar e remover metadados. 

- **Limpeza de datas<sup>1</sup>**: `clean_per_date` remove a data de publicação do texto principal, constantemente presente quando no corpo do texto há os metadados.

- **Limpeza de caracteres especiais**: `clear_per_special_characters` remove caracteres como `-`, `|` e `—` que podem estar presentes no texto, mas não contribuem para a análise semântica. Necessário inserir espaços entre os hífens para evitar remoção de palavras com hífen.

- **Limpeza de fonte<sup>1</sup>**: `clear_source_on_start` remove a fonte de onde foi tirada a notícia do início do texto, caso esteja presente, para evitar que informações de fonte sejam confundidas com o conteúdo da notícia.

- **Limpeza de Hora<sup>1</sup>**: `clean_per_hour` remove a hora de publicação do texto principal, constantemente presente quando no corpo do texto há os metadados.

<sup>1</sup>Essas funções de limpeza podem apresentar um risco ao remover palavras/informações que sejam parte do texto, mas para esse conjunto de dados pequeno, a ocorrência dessas situações é apenas em metadados. Para um conjunto de dados maior, seria interessante criar uma função mais robusta para identificar e remover metadados.

**Obs.1** : As etapas de limpeza pode ser realizado de forma independente do processo principal do programa.

**Obs.2** : Ao executar esse script, o arquivo `noticias_limpa.json` será criado na pasta `data/`.

**Obs.3** : A execução do script `clean_data.py` gera uma pasta `logs/`, a cada processo de limpeza será criado um arquivo de log com o nome `cleaning_log_{data_e_hora}.txt`, onde serão registradas informações sobre o processo de limpeza, como o número de notícias processadas, o número de notícias limpas e detalhes sobre as transformações realizadas.