# One-Slide Version: Why GraphRAG Instead of Plain RAG for Low-Resource Cultural MT

## Slide Title

**Why We Choose GraphRAG Instead of Plain RAG for Cultural Knowledge Support in Low-Resource MT**

## Slide Content

### 1. Why plain RAG is weak for this task

- Plain RAG relies mostly on embedding similarity
- In low-resource settings, rare Khmer cultural terms are poorly represented in embedding space
- Similarity-based retrieval often returns text that is close in meaning, but wrong in culture
- It cannot model important relations well, such as:
  - festival -> ritual
  - kinship term -> age / family side
  - food name -> local alias / forbidden translation
- Result: fluent but culturally wrong translation
- Real examples from our GPT-4o evaluation:
  - `Chol Chnam Thmay` -> `Tet Nguyen Dan`
  - `Achar duki` -> `thay Yuki`
  - Khmer food names -> familiar Vietnamese foods
  - Khmer in Vietnam -> Cambodia

### 2. Why GraphRAG is stronger for this task

- GraphRAG adds structure, not only similarity
- It stores cultural knowledge as:
  - entities
  - relations
  - aliases
  - constraints
- It helps preserve rare but important cultural entities
- It supports explicit reasoning such as:
  - `not equivalent to`
  - `used in ritual`
  - `preferred translation`
  - `community-specific meaning`
- This is especially useful for low-resource MT, where data is sparse but relations are rich
- Main benefit: better cultural grounding, better consistency, fewer identity and entity errors

## Short Speaker Script

This slide gives the main reason we choose GraphRAG over plain RAG.

On the left side, plain RAG is weak because it depends heavily on embedding similarity. In low-resource translation, especially with Khmer cultural terms, embeddings are often not strong enough to represent rare entities correctly. As a result, the system retrieves text that is similar on the surface, but culturally wrong. That is why we see errors such as `Chol Chnam Thmay` becoming `Tet Nguyen Dan`, or `Achar duki` becoming `thay Yuki`.

On the right side, GraphRAG is stronger because it adds structured knowledge. Instead of only retrieving similar text, it retrieves entities, relations, aliases, and constraints. This is important because cultural meaning is relational. A festival is connected to rituals. A kinship term depends on age and family side. A food term may have local aliases and forbidden translations. So for low-resource machine translation, GraphRAG is stronger because it gives the model cultural grounding, not only semantic similarity.

## One-Sentence Closing

**Plain RAG retrieves similar text, but GraphRAG retrieves structured cultural meaning.**
