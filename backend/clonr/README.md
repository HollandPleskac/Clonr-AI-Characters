# Clonr

This package contains the tools and code required to build a functional AI clone. For a notebook that steps through creating an eample clone, please see `nb.ipynb`

## LLMs

LLMs must expose at the minimum, a `generate` method, that takes text as input and returns text as output. The idea is that the intermediate step is a large language model (LLM), but in principle you can just return garbled nonsense and you'll still satisfy the LLM class.

Modern LLMs are built in two phases: (1) expensive pretraining costing 10s of millions of dollars and (2) inexpensive fine-tuning on much smaller selection of data. There can be more phases if you go into Reinforcement learning from Human Feedback (RLHF) territory, but this is essentially it. The 2nd phase is important because it introduces certain formats to guid the LLM, which we call prompt templates. As example, an instruction tuned LLM might require the following format
```text
### Instruction:
(...)

### Response:
(...)
```
And will give unpredictable answers else-wise.

There are generally two types of prompts: chat and non-chat. Chat prompts break into messages, and have something like alternating User and Assistant messages
```text
### User:
...

### Assistant:
...

(continues for a while)

### User:
...

### Assistant:
...
```

Our templates assume this form, and since each template is specific to that llm, require adding attributes to the llm to ensure that the write template is used. Examples are llm.user_start and llm.user_end.

## Theory

In this section we describe some of the algorithms and ideas that we use to build our clone. Specifically, 

### Information retrieval

Fundamentally, there are two operations at play: __get__ and __create__. The first is optimizing for how quickly you can get the info you want, and the second is optimizing for how long it takes to add new information. You can think of the optimal create being just dump into a list, meaning the get is worst case scanning the entire index. In the opposite regime, you can imagine assigning every possible query to a lookup table telling it exactly which item to grab, but this would obviously take an infinitely long time to do (infinite number of possible queries)

### Problem statement

Here, we will phrase the problem statement and give some possible LLM based solutions. Our approach is similar to Llama-index in that we want to use LLMs to answer questions, but slightly different. The problem statement is this:

__Problem statement:__ given a long-form document what is the best way to persist that information, such that it can be effectively queried to provide context to an LLM?

The question can be refined further, to gauge accuracy on different downstream tasks such as
1. Queries pertaining to fact retrieval.
* Shorter, sentence based chunking might work best, as they are most likely to encompass a fact without noise.
* BM25 and other methods can work very well here, when looking for specific things like "what was the price of MSFT on june 8th 2013?".
* In a sense, this is the easiest task, and normal chunking is usually sufficient.
2. Multi-fact retrieval.
* These queries contain information from several chunks potentially. Example - "What events led to world war I?". We can partially solve this by retrieving more chunks for our LLM context, and hope we cover everything.
* See the next point for downsides.
3. High-level query about general topics.
* Queries that require drawing inference from a collection of facts. For example, the previous query - "What were the main causes of world war I?" - may require synthesizing several events in the dataset, then deciding whether or not they contribute to the question.
* Queries that require cause-effect. Example - "What happened on the night of October 13th 2003?". If the passage says, "I bought a lottery ticket that night.", but later on, the document says "That ticket won, and I became a billionaire overnight", then a correct answer would be "I bought a __winning__ lotter ticket".
4. Semantic retrieval.
* Questions like "how does the author feel about this or that". No single chunk will give the right answer here

Each of these are difficult to solve in their own right. There is a sort of grand-unified solution for all of these though, _get a bigger context_. However, perfomance could actually degrade by doing that due to noise and issues with long-form attention. Latency would also be an issue as well as cost.

A second solution, would be to _effectively_ call the LLM on the entire document everytime. Llama-index takes this approach, where they progressively refine the query answer by chunking the document and calling the LLM multiple times. Fuck that, also costly, slow, and not ideal.

The solution we are looking for is a way to pre-compute something like the 2nd solution, and to use that to enhance retrieval and context. We have a few solutions. We will list all of them.

### LLM Indices

We list a bunch of candidate indexing solutions, some using LLMs, some not. All of these solutions use a VectorDatabase in some capacity.

1. __No index. Vector search retrieval__
* Basic method.
* Great for pure fact retrieval, and fantastic when those facts are precise.
* Chunk size and overlap should be optimized to fit the query task (hard to know beforehand and can require specializing the DB to what you think the queries will look like)
* Fast, no LLM cost
* Can use a cross-encoder to re-rank retrieval to further improve results
* can also attempt to create diversity by maximizing the separation of retrieved results

2. __No index. Full document LLM refinement__
* At query time, run the LLM over entire document in chunks, further refining the query each time.
* Heavy cost, unable to parallelize at runtime
* Errors can compound if the LLM misses early
* No way to perform  early stopping if later information proves irrelevant to query.

3. __List index. Precompute LLM causal-summarization__
* We keep a running summary of the document, incrementally building it. If we define the $n$th summary as $a_n$, and the content of the $n$th chunk as $c_n$, The equation looks like $$a_{n+1} = \text{OnlineSummarize}(c_n, a_n), \;\;\; a_0 = c_0$$
* This is basically the same as using the LLM as an RNN, whereby the inputs, outputs, and hidden state are all given by natural language.
* At run time, we run $\text{QueryWithContext}(q_n, a_n)$, and pair each retrieved passage with the necessary context for it.
* Can solve problems where information in chunks need to know what happened before. Example would be "he scored 50 points, with 12 rebound and 30 assists in that game". The summary might tell you who "he" is and what the game was.

4. __List index. Precompute LLM causal-summarization. Aggregrate chunks and embed with Summary__
* First aggregate chunks into bigger pieces $b_0, \ldots, b_k = \text{Aggregate}(c_0, \ldots, c_n)$ (k << n. the n vs k stuff is wrong below.)
* Run causal summarization as in (3) and compute $a_{n+1} = \text{OnlineSummarize}(c_n, a_n), \;\;\; a_0 = c_0$
* Summarize each chunk $b_n$, using its information and the context from the above causal summaries. $$s_n = \text{SummarizeWithContext}(b_n, s_n)$$
* Embed the summaries $b_n$, and use those for retrieval on $b_n$.
* The pros here are that we can do better high-level retrieval, but the cons are we are stuck with retrieving bigger chunks, and this can go wrong if the summaries are cracked.

5. __Tree index. Precompute LLM tree of summaries.__
* As above, run $c^{(1)}_0, \ldots, c^{(1)}_k = \text{Aggregate}(c_0, \ldots, c_n)$ to get bigger chunks (k << n)
* Perform normal summarization on each chunk (no online context stuff) $c^{(1)}_i = \text{Summarize}(c_i)$
* Repeat until there is just one remaining chunk, which is the root node, and contains a summary of the entire document
* pros are can be parallelized, n lg n complexity for number of LLM calls (n is number of chunks)
* cons are that summaries could be broken for later tree elements, as they may depend on the context

6. __Tree index. Precompute LLM tree of causal summaries.__
* similar to the above, but replace $\text{Summarize}$ with $\text{SummarizeWithContext}$. Since these are summaries, we can just recursively output the result
* $c^{(i)}_n = \text{SummarizeWithContext}(c^{(i)}_n, c^{(i+1)}_{n-1})$. In words, summarize a chunk, and feed that to its neighbor along with its neighbor's content to summarize the neighbor chunk. Repeat.
* pros we get the context we were missing
* cons it's now sequential, but whatever.

7. __Tree index. (however it's constructed) Tree queries__
* Once we have the tree index, in theory we can query any node. However, these will likely give redundant results.
* In general it might make sense to return a tree-structure response. This would be a concatenation of all summaries along a path from root to leaf. If you have a tree depth of $D$ and average number of children per node of $C$, your response will have a redundancy factor (i.e. the amount of info I already knew from the parent summary) of about $1/C$. We can think about this as saying about $(1/C)$ percent of the info we already knew from the summary.
* We can query the _leaves_ with highest similarity, then return the path to the root
* We can start at the root, and perform a beam search until we find the paths to roots with the highest similarity. I (Jonny) actually ran something similar to this in the past, and you run into problems when there are paths with different lengths (longer paths get screwed). This can also fail if the summaries do not contain some specific detail, i.e. this is fucked when you want fact retrieval.


### Token cost

Define the following values:
__N__: the number of tokens in the document
__context_size__: the number of tokens in the context of each LLM call
__summary_size__: the max number of tokens output for a summary (this will make an upperbound on LLM calls. Shorter summaries will give us fewer tokens)
__compression_ratio__: pretty simple, just context_size / summary_size. How much we reduce at each turn.


1. Long-context (N tokens + summary_size)
* This is the lower bound. You have to ingest at least N tokens

2. List index, causal summary (N + 2 * N / compression_ratio)
* You ingest all tokens, but for each chunk you add summary_size tokens to it
* this adds 2 * summary_size * (N / context_size) which is 2 * N / compression
* the factor of 2 comes from completion tokens creating the summary as well.

3. List index, big chunks, summary as embedding (N + N / compression_ratio)
* similar to above, but without the causal part we don't double count summaries.

4. Tree index (N * (1 + 1 / compression_ratio) * log_{compression_ratio}(N))
* At each step, we reduce the size of the entire document by a factor of compression_ratio, and spend an entire document worth of tokens to do it.
* The answer is keep adding the above until you get to N <= summary_size.
* 
```python
def tree_tokens_upper_bound(doc_size: int, context_size: int, summary_size: int):
    r = context_size / summary_size
    total = 0
    while doc_size > summary_size:
        compression_factor = round(doc_size / r)
        # below can be written doc_size (1 + 1 / r)
        total += doc_size + summary_size * round(doc_size / context_size)
        doc_size = round(doc_size / r)
    return total
```

5. Tree index with causality (N * (1 + 2 / compression_ratio) * log_{compression_ratio}(N))
* same as above, but double the summaries.


## Database systems.

Clones make use of the following database systems.

1. Vector database. This is for performing similiarity search with a bi-encoder paired with a distance metric (cosine, euclidean) on a large corpus of vectors. In this case, our vectors are primarily text. Multimodal is not the goal here.
2. Relational database. Typical relational stuff, useful for storing messages, wiki facts, items like documents that collect a bunch of document chunks. This is also storage method used for more comlicate graph data structures (trees, lists) created by our indexing.
3. In-memory caching. Used for fast memory retrieval, and retrieval of dynamic memory, which has high read-write access.

Databases are stored under `clonr.storage`. We provide a simple in-memory vectordb for running locally, that performs exact similarity search. We also provide a relational sqlite db for testing persistent storage. The downside is that pgvector unifies these, so the flow is not too similar to production. Also, sqlite is annoying about uuids.

## Retrieval

There are two types of similarity score
1. bi-encoder distance computation. check the distance between query vector and all database vectors
2. cross-encoder reranking. select the top K from (1), then re-rank similarity with a slower, but more powerful cross-encoder that takes in both arguments (so it learns a new distance metric other than e.g. cosine) like CrossEncoder(query, passage) => score.

On top of that, we also build the GenerativeAgentsRetriever, which uses the retrieval method from their paper. It ranks according to the formula
$$
\text{score} = \alpha_recency * \text{recency} + \alpha_importance * \text{importance} + \alpha_relevance * \text{relevance}
$$
The default $\alpha$ values are 1. Recency is given by exponential decay with some factor $\gamma \in [0, 1]$ as $\gamma^t$. 1 means no time decay, and 0 means disregard time. Importance is computed via an LLM at storage time, and relevance is just the similarity score above, normalized to [0, 1] (cross-encoders need to apply a sigmoid, and cosine distance is like 1 - dist.).

The above method fails in a typical vectordb, since you can't perform a combined search, but it succeeds in pgvector!

## Text Splitting

we have 3 options, sentence-level, token-level, character-level. The last option is the fastest, the middle is slower but will give more manageable outputs for downstream tasks that require token count, like embedding and LLM calls. The first has the highest accuracy if done correctly, but also many pitfalls. Chunks are uneven length as sentence lengths are variable, and it is designed only for English, as it relies on rules to determine when to end a sentence (spacy uses a model, but is slower and not worth it, nltk is rule-based).

The two main parameters here are `chunk_size` and `overlap_size`. The former is the size of chunks that will be embedded and stored in a vector database. The latter is a guard against a bad naive splitting, i.e., what are the odds that we chop out important context. As an example, imagine a query, "Who is president of the U.S." retrieves a chunk "Jonny is president of the". If the following chunk is "Society of Physics Students", then you got an unlucky chunk that destroyed a critical part of the sentence. Your overlap size should be the maximum size that you believe two pieces of relevant information can be separated by in a document. Other examples are coreference resolution, i.e. resolving pronouns when you don't have the previous text that told you who "he, she, they" refers to. Again, think how long you can go with "he, she, they" before resolving. In some kinds of text, the answer is the entire document, in which case you should use the more advanced indexing methods discussed above for adding a global context to retrieval.


## Clone

This is the main stuff. How do we actually build a functioning AI bot? 

### Inference
Inference is done via LLM, which means the main object is the prompt. Roughly, the prompting is broken down into the following order/scheme.

1. system_prompt (designed for this task)
2. name
3. short_description
4. long_description
5. example_dialogues
6. agent_summary
7. memories
7.5. Wiki/facts?
8. entity_context_summary
9. conversation_messages

__TODO__ (Jonny): I fucking forgot about wiki/facts retrieval. shiiiiit. Need to figure out where this goes!

The first 4 are static, and retrieved from the relational database. (5) uses a vector db retrieval for relevance from a static collection of example dialogues (maybe rethink this in the future?). (6) is retrieved every turn from the cache and synthesized periodically, when a certain importance criteria is met, via llm calls. (7) is a vector database retrieval with special retrieval function. (8) is retrieved from cache and also synthesized periodically like (6). (9) is retrieved from cache and just lists the recent messages.

### Storage
Some of the pieces above are dynamic and change over time. A critical component of our system is ensuring these update appropriately and timely. the agent and context summaries follow a 2-step process, of query the memory stream (vectordb) for relevant information, followed by an LLM call to use that as context for refining the current summaries.

The memory stream contains the agent's interactions with the world, including messages sent and received. More importantly, it implements a recursive bottoms-up tree structure that makes use of _reflections_ to recursively form memories based on other memories and reflections (i.e. the recursive bit). Memory formation is similar to the synthesis part above, in that it triggers upon certain events. In this case, the event is when the importance scores of the memory stream pass a certain threshold.

Reflections are generated in a 3-part process
1. LLM call: what are the most important things about the last 100 messages?
2. query the output of the above call against memory stream to obtain all relevant memories (beyond the last 100!)
3. synthesize the result into reflections and store as memories with depth > 0. (there is another step of forming edges, but it's actually not necessary beyond being nice for later inspection of the memory tree.)

### Planning
lol we aren't doing planning. But this basically sets goals, motives, and objective for the agent to complete. We don't do this, since it adds many LLM calls + complexity, and does not make sense when the agent is not living in an environment with a running clock. If time doesn't move forward, it's hard to plan goals

### External sources
A crucial aspect of our pipeline is allowing users and creators to influence their clone dynamically. These appear in the form of "internal thoughts" which are just memories stated without the tint of observationality. These are statements like "I'm happy" or "I don't know what to eat for dinner". These integrate seamlessly with the memory stream, allowing people to hook up 3rd party sources of info, such as social media, that can pubsub update all clones with recent information. This part is cooooool.