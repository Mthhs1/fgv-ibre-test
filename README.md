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

