# One-Slide Detailed Version: Why GraphRAG Instead of Plain RAG for Low-Resource Cultural MT

## Slide Title

**Why We Choose GraphRAG Instead of Plain RAG for Cultural Knowledge Support in Low-Resource Khmer-Vietnamese MT**

## Slide Content

### 1. Why plain RAG is weak for this task

- Plain RAG depends mainly on **embedding similarity**
- In our setting, **Khmer and Khmer Krom are grammatically very similar**
  - the main difficulty is **not sentence structure**
  - the main difficulty is **cultural entities and community-specific meanings**
- This makes chunk-level similarity less useful, because the model may retrieve text with similar grammar but **wrong cultural grounding**
- Low-resource retrieval is even harder because:
  - rare Khmer cultural terms are weakly represented in embedding space
  - transliterations and aliases are inconsistent
  - online Khmer-Khmer Krom cultural resources are very limited
- As a result, plain RAG often retrieves text that is semantically close but culturally incorrect
- Real GPT-4o error patterns:
  - `Chol Chnam Thmay` -> `Tet Nguyen Dan`
  - `Achar duki` -> `thay Yuki`
  - Khmer food names -> familiar Vietnamese foods
  - Khmer in Vietnam -> Cambodia

### 2. Why GraphRAG is stronger for this task

- GraphRAG adds **structured cultural grounding**, not only semantic similarity
- It models knowledge as:
  - entities
  - relations
  - aliases
  - constraints
  - provenance
- This is a better fit for our task because:
  - Khmer and Khmer Krom differ most at the **entity level**
  - cultural meaning depends on relations, not only text proximity
  - scarce internet data can still be turned into a reusable knowledge structure
- GraphRAG can explicitly encode:
  - `festival -> ritual`
  - `kinship term -> age / family side`
  - `food -> local alias / forbidden translation`
  - `community -> distinct from Cambodia`
  - `entity -> not equivalent to common Vietnamese term`
- Main benefit:
  - better cultural fidelity
  - better consistency across translations
  - fewer identity, ritual, and entity errors

## Speaker Script

This slide explains why plain RAG is not enough for our Khmer-Vietnamese translation task, and why GraphRAG is more suitable.

On the left side, plain RAG is weak mainly because it relies on embedding similarity. In our case, Khmer and Khmer Krom are already very similar in grammar and sentence structure, so the main difficulty is not general fluency. The real difficulty lies in rare cultural entities, community-specific meanings, ritual roles, kinship systems, and local identity. That means chunk similarity is often not enough. A retrieved passage may look semantically relevant, but still be culturally wrong.

This problem becomes worse because the task is low-resource. Rare Khmer terms are poorly represented in embedding space, transliterations are inconsistent, and reliable online resources are limited. So plain RAG often retrieves weak or misleading evidence. That is why we see errors such as `Chol Chnam Thmay` being translated as `Tet Nguyen Dan`, or `Achar duki` becoming `thay Yuki`.

On the right side, GraphRAG is stronger because it adds structure. Instead of relying only on text similarity, it stores cultural knowledge as entities, relations, aliases, constraints, and provenance. This is exactly what we need, because the difference between Khmer and Khmer Krom is concentrated at the entity level. GraphRAG lets us encode relations such as festival to ritual, kinship term to age and family side, food term to local alias, and community identity as distinct from Cambodia. Even when internet data is scarce, we can still turn small but valuable knowledge sources into a reusable graph. So GraphRAG gives us better cultural grounding, better consistency, and fewer cultural translation errors.

## One-Sentence Closing

**In this task, grammar is not the main bottleneck; cultural entities are. That is why GraphRAG is more suitable than plain RAG.**
