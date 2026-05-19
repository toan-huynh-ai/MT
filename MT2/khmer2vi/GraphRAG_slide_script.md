# Why We Choose GraphRAG Instead of RAG to Build Cultural Knowledge Base Supporting Low-Resource Machine Translation

## How to use this file

- Each section below is one slide.
- `Slide content` can be copied directly into presentation slides.
- `Speaker script` is a detailed script you can speak during the presentation.
- The content is written in English and tailored to the Khmer-Vietnamese low-resource MT setting.

---

## Slide 1. Title Slide

### Slide content

- **Why We Choose GraphRAG Instead of RAG to Build Cultural Knowledge Base Supporting Low-Resource Machine Translation**
- Case study: Khmer-Vietnamese cultural translation
- Focus: cultural entities, low-resource retrieval, and translation reliability

### Speaker script

Hello everyone. Today I will explain why we choose GraphRAG instead of standard RAG to build a cultural knowledge base for low-resource machine translation.

Our case study is Khmer-to-Vietnamese translation, especially culturally rich data from Khmer communities in Vietnam. In this setting, the main challenge is not only translating words into fluent Vietnamese, but also preserving cultural meaning, ritual roles, kinship relations, food names, and local identity.

The main argument of this presentation is simple: for low-resource machine translation, especially cultural translation, the problem is not only missing text, but missing structured knowledge. That is why GraphRAG becomes more suitable than plain RAG.

---

## Slide 2. The Core Problem in Low-Resource Cultural MT

### Slide content

- Low-resource MT is not only a language problem
- It is also a **knowledge grounding problem**
- Cultural translation requires:
  - correct entity recognition
  - correct relation understanding
  - correct community identity
- Many errors come from missing structure, not missing fluency

### Speaker script

To begin, we need to define the real problem.

In low-resource machine translation, people often focus on the lack of parallel data. That is true, but for cultural translation, the deeper issue is knowledge grounding.

When translating Khmer into Vietnamese, especially in cultural interviews or ethnographic material, the model must know much more than vocabulary. It must know what a festival is, what a ritual role is, how a kinship term works, whether a food name should be translated or preserved, and whether a term belongs to Khmer in Vietnam or to Cambodia in general.

So the challenge is not only generating fluent output. The challenge is grounding the output in the correct cultural system.

This is why a simple retrieval approach is often insufficient.

---

## Slide 3. What We Observed from GPT-4o Errors

### Slide content

- GPT-4o is often fluent, but not always faithful
- Common real errors in our Khmer-Vietnamese experiments:
  - cultural entity substitution
  - ritual domestication
  - kinship flattening
  - identity shift
- Examples:
  - `Chol Chnam Thmay` -> `Tet Nguyen Dan`
  - `Achar duki` -> `thay Yuki`
  - Khmer in Vietnam -> Cambodia
  - Khmer food names -> more familiar Vietnamese foods

### Speaker script

Before discussing architecture, let us look at the actual translation problem.

From our evaluation, GPT-4o often produces fluent Vietnamese, but the output is not always culturally faithful.

We observed several recurring error types.

The first is cultural entity substitution. A Khmer cultural item is replaced by a more familiar Vietnamese item.

The second is ritual domestication. A Khmer religious or festival term is normalized into a majority-culture term.

The third is kinship flattening. A rich Khmer kinship expression is simplified into a generic Vietnamese form such as older brother or younger sister.

The fourth is identity shift. Instead of referring to Khmer communities in Vietnam, the model shifts toward a more general Cambodia-centered interpretation.

For example, `Chol Chnam Thmay` becomes `Tet Nguyen Dan`. `Achar duki` becomes `thay Yuki`. Some Khmer food names are mapped into familiar Vietnamese foods. These errors show that the model is not simply missing words. It is missing the structure behind those words.

---

## Slide 4. Why Standard RAG Is Not Enough

### Slide content

- Standard RAG depends heavily on **embedding similarity**
- It works well when:
  - the language is well represented
  - entities are common
  - meanings are explicit in text chunks
- It struggles when:
  - entities are rare
  - spellings vary
  - transliterations are inconsistent
  - meaning depends on relations, not just nearby text

### Speaker script

Now let us discuss why standard RAG is not enough.

RAG usually works like this: we embed the query, embed the document chunks, and retrieve the chunks that are closest in vector space.

This works well when the language is well represented in training data, when the entities are frequent, and when the relevant meaning is already written clearly in one or two text chunks.

However, our data does not look like that.

In Khmer-Vietnamese cultural translation, many important terms are rare. Their spellings vary. They may appear in Khmer script, Latin transliteration, Vietnamese explanation, or mixed forms. In many cases, meaning is not stored in one chunk. Meaning comes from relations: this ritual belongs to this festival, this term is not equivalent to that term, this kinship label depends on age and marriage relation.

That is exactly where standard RAG becomes weak.

---

## Slide 5. Why Embedding-Centered Retrieval Is Fragile in Low-Resource Settings

### Slide content

- Low-resource embedding models often suffer from:
  - low coverage of rare cultural terms
  - unstable tokenization and segmentation
  - weak alignment for transliterated forms
  - bias toward high-resource languages and concepts
- Result:
  - retrieval returns “similar” but culturally wrong evidence
- Example:
  - a Khmer New Year term may retrieve generic New Year content

### Speaker script

This slide is very important, because it explains the low-resource aspect.

In low-resource settings, embedding-based retrieval is fragile for several reasons.

First, rare cultural terms often have poor coverage in multilingual embedding models. The model has simply seen them too few times.

Second, Khmer tokenization and segmentation are more difficult than high-resource languages, so vector representations may be unstable.

Third, transliterated forms are inconsistent. The same entity may appear in Khmer script, in Vietnamese phonetic spelling, in English-style transliteration, or in noisy mixed text.

Fourth, multilingual models are biased toward high-resource languages and high-frequency concepts. So if a Khmer term is rare, the embedding space may pull it toward a more common but culturally incorrect concept.

That means retrieval may return chunks that look semantically similar on the surface, but are culturally wrong.

For example, a Khmer New Year festival term may retrieve generic New Year material rather than Khmer-specific ritual information.

---

## Slide 6. What GraphRAG Changes

### Slide content

- GraphRAG reduces dependence on embedding-only similarity
- It adds **structured knowledge**:
  - entities
  - relations
  - aliases
  - constraints
  - provenance
- It retrieves a **subgraph**, not only text chunks
- It supports reasoning such as:
  - belongs to
  - not equivalent to
  - translation preference
  - community-specific usage

### Speaker script

So what does GraphRAG change?

GraphRAG does not only retrieve similar chunks. It retrieves structured knowledge.

Instead of storing knowledge only as text segments, we represent important information as entities and relations. For example, a node can be a festival, a food, a ritual role, a kinship term, or a community identity. Edges can represent relations such as belongs to, used in, related to, not equivalent to, preferred translation, or restricted usage.

This matters because it gives the model something more stable than similarity.

When the system sees a query containing a rare term, it can link that term to a canonical node, retrieve its aliases, relations, and translation notes, and then pass that structured evidence to the translation model.

So GraphRAG helps us move from approximate similarity to structured grounding.

---

## Slide 7. Why GraphRAG Fits Cultural Knowledge Better Than RAG

### Slide content

- Cultural knowledge is relational by nature
- Examples of useful graph relations:
  - `festival -> has_ritual -> ritual`
  - `role -> used_in -> funeral`
  - `kinship_term -> depends_on -> age`
  - `food -> has_alias -> local spelling`
  - `entity -> not_equivalent_to -> common Vietnamese term`
- GraphRAG is better when meaning depends on system-level relations

### Speaker script

The reason GraphRAG is especially suitable here is that cultural knowledge is relational by nature.

A festival is not just a name. It has rituals, objects, participants, timing, and symbolic meaning.

A kinship term is not just a label. It depends on age, marriage relation, generation, gender, and social respect.

A food term is not just a noun. It may have local spellings, preparation practices, ritual use, and identity meaning.

GraphRAG is a natural fit because it stores these relations explicitly.

For example, we can encode that a festival has a ritual, that a ritual role is used in funerals, that a kinship term depends on age, that a food has multiple aliases, and that a Khmer entity is not equivalent to a more common Vietnamese term.

This is much harder to capture reliably with chunk-based retrieval alone.

---

## Slide 8. How GraphRAG Can Reduce Real GPT-4o Errors

### Slide content

- Error 1: `Chol Chnam Thmay` -> `Tet Nguyen Dan`
  - Graph fix: store `not_equivalent_to` relation
- Error 2: `Achar duki` -> `thay Yuki`
  - Graph fix: store ritual role node + aliases + funeral relation
- Error 3: Khmer kinship flattened into generic Vietnamese
  - Graph fix: encode age, relation, marriage side, generation
- Error 4: Khmer food names replaced by familiar Vietnamese foods
  - Graph fix: canonical food node + alias table + forbidden mapping

### Speaker script

This slide connects architecture to real translation errors.

First, consider the case where `Chol Chnam Thmay` is translated as `Tet Nguyen Dan`. A graph can explicitly encode that this Khmer festival is not equivalent to Tet. It may be similar as a New Year festival, but it is not the same entity.

Second, consider `Achar duki` becoming `thay Yuki`. This happens because the model sees a rare term and hallucinates a familiar-looking form. In a graph, `Achar duki` would be a ritual-role node with aliases, religious context, and funeral relations, making hallucination less likely.

Third, kinship flattening can be reduced by encoding features such as older or younger, maternal or paternal side, spouse side, and generation level.

Fourth, food-name substitution can be reduced by maintaining canonical food nodes, local aliases, ingredient relations, and forbidden translations.

So the main advantage of GraphRAG is not only better retrieval. It is better control over culturally sensitive translation decisions.

---

## Slide 9. Why GraphRAG Is Especially Valuable for Low-Resource Data

### Slide content

- Low-resource data is often:
  - sparse
  - fragmented
  - inconsistent
  - rich in local knowledge
- GraphRAG helps by:
  - merging scattered evidence into one structure
  - normalizing aliases and variants
  - preserving rare but important entities
  - improving consistency across translations

### Speaker script

Now let us return to the low-resource question directly.

Low-resource data is not only small. It is often fragmented and inconsistent. Useful knowledge may be distributed across interview transcripts, glossaries, field notes, annotations, and small bilingual examples.

This means the problem is not just lack of data volume. The problem is lack of data organization.

GraphRAG is valuable because it can merge scattered evidence into one structure. It can normalize aliases, preserve rare entities, and keep the same entity consistent across many translation examples.

That is a major advantage in low-resource settings, where every rare cultural term matters more than in high-resource settings.

In other words, low-resource conditions make structure more valuable, not less valuable.

---

## Slide 10. But GraphRAG Is Not Free

### Slide content

- GraphRAG also has costs:
  - harder to build
  - harder to maintain
  - requires entity schema and relation schema
  - requires linking and normalization
- Risks:
  - wrong graph = strong but wrong grounding
  - over-structuring may lose nuance from text
- Best practice: **GraphRAG should complement, not replace, text evidence**

### Speaker script

Of course, GraphRAG is not free.

It is more difficult to build than plain RAG. We need an entity schema, a relation schema, alias normalization, entity linking, provenance tracking, and update logic.

There is also a risk: if the graph is wrong, the system may become confidently wrong. Bad structure can be more dangerous than no structure.

Another limitation is that some kinds of meaning are better preserved in text than in graph form. Narrative detail, social nuance, discourse style, and example sentences should still come from textual evidence.

So the best practice is not to replace text entirely. The best practice is to let GraphRAG handle structured cultural knowledge while text retrieval still provides examples and explanation.

---

## Slide 11. Recommended System Design

### Slide content

- **Recommended hybrid pipeline**
- Layer 1: glossary and terminology constraints
- Layer 2: GraphRAG for cultural entities and relations
- Layer 3: text RAG for examples and discourse context
- Layer 4: translation model with controlled prompt
- GraphRAG is the cultural backbone, not the only component

### Speaker script

Based on our findings, I do not recommend using GraphRAG alone.

The best design is a hybrid pipeline.

First, we need a glossary layer. This includes canonical translations, aliases, and forbidden mappings.

Second, we use GraphRAG to store structured cultural knowledge: festivals, rituals, kinship systems, foods, communities, places, and their relations.

Third, we keep a text RAG layer to retrieve real bilingual examples, discourse context, and extended explanations.

Fourth, all of this is passed into the translation model with a controlled prompt.

In this design, GraphRAG is the cultural backbone of the system, but not the only component.

---

## Slide 12. Final Takeaway

### Slide content

- We choose GraphRAG over plain RAG because:
  - low-resource translation needs structure, not only similarity
  - cultural entities depend on relations, not only text proximity
  - embedding-only retrieval is fragile for rare Khmer terms
  - GraphRAG improves consistency, grounding, and cultural fidelity
- Final message:
  - **For cultural low-resource MT, GraphRAG is not just a retrieval upgrade. It is a knowledge representation upgrade.**

### Speaker script

To conclude, we choose GraphRAG over plain RAG because low-resource cultural translation needs more than similarity search.

It needs structure. It needs stable entities. It needs explicit relations. And it needs the ability to preserve identity and cultural meaning even when the terms are rare.

Plain RAG is useful, but embedding-only retrieval is too fragile for many Khmer cultural terms.

GraphRAG gives us a better foundation for grounding translation decisions in structured knowledge. It improves consistency, reduces entity distortion, and gives us better control over culturally sensitive translation.

So the final message is this: for low-resource cultural machine translation, GraphRAG is not only a retrieval upgrade. It is a knowledge representation upgrade.

Thank you.

---

## Optional Backup Slide A. Concrete Node Types for Khmer-Vietnamese Cultural Graph

### Slide content

- Possible node types:
  - Festival
  - Ritual
  - Ritual role
  - Kinship term
  - Food
  - Ingredient
  - Community
  - Place
  - Alias
  - Translation note

### Speaker script

If needed, we can design the graph with node types such as festival, ritual, ritual role, kinship term, food, ingredient, community, place, alias, and translation note.

This would let the system retrieve both the entity itself and the cultural context around it.

---

## Optional Backup Slide B. Example of a Useful Graph Constraint

### Slide content

- Example:
  - `Chol Chnam Thmay`
  - `type: Khmer festival`
  - `community: Khmer in Vietnam / Khmer cultural context`
  - `related ritual: Buddha bathing`
  - `not_equivalent_to: Tet Nguyen Dan`
  - `preferred translation: keep original term + short explanation`

### Speaker script

This is one example of how a graph can encode a culturally important constraint.

Instead of relying on similarity alone, we can explicitly say that `Chol Chnam Thmay` is a Khmer festival, linked to Khmer cultural practice, related to specific rituals, and not equivalent to Tet Nguyen Dan.

That one constraint alone can prevent a major category of translation errors.

---

## Optional Backup Slide C. One-Sentence Summary for Q and A

### Slide content

- **RAG retrieves similar text. GraphRAG retrieves structured cultural meaning.**

### Speaker script

If I have to summarize the whole presentation in one sentence, I would say this: RAG retrieves similar text, but GraphRAG retrieves structured cultural meaning.
