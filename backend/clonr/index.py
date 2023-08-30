import asyncio
import uuid
from abc import ABC, abstractmethod

from loguru import logger
from opentelemetry import trace
from pydantic import BaseModel, validator

from clonr import templates
from clonr.data_structures import Document, IndexType, Node
from clonr.generate import (
    auto_chunk_size_summarize,
    online_summarize,
    summarize,
    summarize_with_context,
)
from clonr.llms import LLM, MockLLM
from clonr.text_splitters import TextSplitter
from clonr.tokenizer import Tokenizer
from clonr.utils import aggregate_by_length

tracer = trace.get_tracer(__name__)


class TokenEstimate(BaseModel):
    doc_tokens: int
    llm_call_tokens: int
    max_depth: int | None = None
    multiplier: int | None = None
    metadata: dict | None = None

    @validator("multiplier", always=True)
    def set_multiplier(cls, v, values):
        return round(values["llm_call_tokens"] / (1e-4 + values["doc_tokens"]), 2)


def create_leaf_nodes(doc: Document, splitter: TextSplitter) -> list[Node]:
    chunks = splitter.split(doc.content)
    nodes: list[Node] = []
    for i, x in enumerate(chunks):
        node = Node(
            content=x,
            document_id=doc.id,
            index=i,
            is_leaf=True,
            depth=0
            # embedding=embs[i],
            # embedding_model=self.encoder.name,
        )
        nodes.append(node)
    return nodes


# (Jonny): Not currently used.
# async def summarize_with_context(
#     content: str, prev_summary: str, llm: LLM, params: GenerationParams
# ) -> LLMResponse:
#     prompt = templates.SummarizeWithContext.render(
#         passage=content, llm=llm, prev_summary=prev_summary
#     )
#     return await llm.agenerate(prompt, params=params)


class Index(ABC):
    @abstractmethod
    def estimate_llm_tokens(self, doc: Document) -> TokenEstimate:
        pass

    @abstractmethod
    async def abuild(self, doc: Document) -> list[Node]:
        pass

    @abstractmethod
    def build(self, doc: Document) -> list[Node]:
        pass

    @classmethod
    def from_type(cls, type: IndexType, **kwargs):
        if type == IndexType.list:
            return ListIndex(**kwargs)
        if type == IndexType.list_with_context:
            return ListIndexWithContext(**kwargs)
        if type == IndexType.tree:
            return TreeIndex(**kwargs)
        raise TypeError("Invalid index type!")


class ListIndex(Index):
    type = IndexType.list

    def __init__(
        self,
        tokenizer: Tokenizer,
        splitter: TextSplitter,
    ):
        self.tokenizer = tokenizer
        self.splitter = splitter
        self._index: dict[str, Node] = {}

    @property
    def num_nodes(self):
        return len(self._index)

    def estimate_llm_tokens(self, doc: Document) -> TokenEstimate:
        return TokenEstimate(
            doc_tokens=self.tokenizer.length(doc.content), llm_call_tokens=0
        )

    def get(self, id: str | uuid.UUID):
        return self._index.get(str(id))

    @tracer.start_as_current_span("ListIndex_abuild")
    async def abuild(self, doc: Document, **kwargs) -> list[Node]:
        logger.info(f"Building {self.__class__.__name__} on doc_id: {doc.id}.")
        nodes = create_leaf_nodes(doc=doc, splitter=self.splitter)
        for node in nodes:
            self._index[str(node.id)] = node
        doc.index_type = self.type
        doc.text_splitter = self.splitter.name
        doc.max_chunk_size = self.splitter.max_chunk_size
        doc.chunk_overlap = self.splitter.chunk_overlap
        self._index = {}  # TODO (Jonny): trying to make this stateless!
        # No LLM calls in this one :)
        return nodes

    def build(self, doc: Document, **kwargs) -> list[Node]:
        return asyncio.get_event_loop().run_until_complete(
            self.abuild(doc=doc, **kwargs)
        )


class ListIndexWithContext(ListIndex):
    """Implements the OnlineSummarize method. This adds a context
    field to every node, by incrementally summarizing the document
    beginning with the first node.

    Schematically, the procedure is:
    doc => list[Node]
    context_0 = ''
    context_{i+1} = OnlineSummarize(node_i, context_i)

    Note, you could quickly run up costs if you have too many chunks,
    as that will cause a lot of LLM calls! This is a really expensive
    method for small chunk sizes!
    """

    type = IndexType.list_with_context

    def __init__(
        self,
        tokenizer: Tokenizer,
        splitter: TextSplitter,
        llm: LLM,
    ):
        self.tokenizer = tokenizer
        self.splitter = splitter
        self.llm = llm
        self._index: dict[str, Node] = {}
        self._tokens_processed = 0
        prompt = templates.OnlineSummarize.render(
            passage="", prev_summary="", llm=MockLLM("")
        )
        self._prompt_len = self.tokenizer.length(prompt)
        self.max_tokens = (
            4096  # FixMe (Jonny): just put this in for now, until we use this class.
        )

    @property
    def num_nodes(self):
        return len(self._index)

    @property
    def tokens_processed(self):
        return self._tokens_processed

    def estimate_llm_tokens(self, doc: Document):
        # the entire document is ultimately processed
        llm_call_tokens = self.tokenizer.length(doc.content)
        nodes = create_leaf_nodes(doc=doc, splitter=self.splitter)

        # every node can generate up to max_tokens for its summary
        llm_call_tokens += len(nodes) * self.max_tokens
        llm_call_tokens += len(nodes) * self._prompt_len

        return TokenEstimate(
            doc_tokens=self.tokenizer.length(doc.content),
            llm_call_tokens=llm_call_tokens,
        )

    @tracer.start_as_current_span("ListIndexWithContext_abuild")
    async def abuild(self, doc: Document, **kwargs) -> list[Node]:
        logger.info(f"Building {self.__class__.__name__} on doc_id: {doc.id}.")
        nodes = await super().abuild(doc=doc)
        logger.info(f"Running online summarize on {len(nodes)} nodes.")
        kwargs["subroutine"] = self.__class__.__name__
        llm_calls = await online_summarize(
            nodes=nodes,
            llm=self.llm,
            **kwargs,
        )
        for i, call in enumerate(llm_calls):
            nodes[i].context = call.content
            self._tokens_processed += call.usage.total_tokens
        doc.index_type = self.type
        doc.text_splitter = self.splitter.name
        doc.max_chunk_size = self.splitter.max_chunk_size
        doc.chunk_overlap = self.splitter.chunk_overlap
        self._index = {}  # TODO (Jonny): trying to make this stateless!
        return nodes

    def build(self, doc: Document, **kwargs) -> list[Node]:
        return asyncio.get_event_loop().run_until_complete(
            self.abuild(doc=doc, **kwargs)
        )


# TODO (Jonny): If we decide to use this in the future, consider implementing
# text spliter overlapping for each level. Can probably just reuse the _aggregate_with_overlap
# function in text_splitters
class TreeIndex(Index):
    """Implements the TreeSummarize method. This iteratively
    aggregates leaf nodes then distills with an LLM summarization
    call until only one node, the root, remains.

    Schematically, the procedure is:
    doc => list[Node]
    while len(nodes) > 1:
        groups = aggregate(nodes)
        nodes = map(LLM_SUMMARIZE, groups)

    Note, this can fail when the group size is less than 2x the max
    summary size. In this case, you might encounter a situation where
    aggregate(nodes) = nodes, which means that the number of nodes would
    never reduce (group_size = n_nodes).
    """

    type = IndexType.tree

    def __init__(
        self,
        tokenizer: Tokenizer,
        splitter: TextSplitter,
        llm: LLM,
        max_group_size: int | str = "auto",
        max_depth: int | None = None,
    ):
        self.tokenizer = tokenizer
        self.splitter = splitter
        self.llm = llm
        self._index: dict[str, Node] = {}
        self._tokens_processed = 0
        self.max_depth = max_depth

        prompt = templates.Summarize.render(passage="", llm=MockLLM(""))
        self._prompt_len = self.tokenizer.length(prompt)
        if isinstance(max_group_size, str):
            if max_group_size != "auto":
                raise ValueError("Max group size should be an int or auto.")
            max_group_size = auto_chunk_size_summarize(llm=llm)
        self.max_group_size = max_group_size

    @property
    def num_nodes(self):
        return len(self._index)

    @property
    def tokens_processed(self):
        return self._tokens_processed

    def estimate_llm_tokens(self, doc: Document, max_tokens: int = 512):
        # the entire document is ultimately processed
        assert max_tokens < 2 * self.max_group_size
        llm_call_tokens = 0
        depth = 0
        sum_size = max_tokens
        prompt_size = self._prompt_len
        nodes = create_leaf_nodes(doc=doc, splitter=self.splitter)
        chunks = [x.content for x in nodes]
        depth = 0
        metadata: list[dict[str, int]] = [{"depth": depth, "nodes": len(chunks)}]
        depth += 1
        prev_len = len(chunks)
        for _ in range(self.max_depth or len(nodes)):
            if len(chunks) <= 1:
                break
            group_chunks = aggregate_by_length(
                chunks, max_size=self.max_group_size, length_fn=self.tokenizer.length
            )
            groups = ["".join(x) for x in group_chunks]
            for i, g in enumerate(groups):
                llm_call_tokens += self.tokenizer.length(g) + sum_size + prompt_size
                groups[i] = "x " * (sum_size - 1)
            chunks = groups
            metadata.append({"depth": depth, "nodes": len(chunks)})
            depth += 1
            if len(chunks) == prev_len:
                raise ValueError(f"Failed to reduce chunks ({prev_len} -> {prev_len})")
        return TokenEstimate(
            doc_tokens=self.tokenizer.length(doc.content),
            llm_call_tokens=llm_call_tokens,
            max_depth=depth,
            metadata={"layers": metadata},
        )

    @tracer.start_as_current_span("_process_level")
    async def _process_level(
        self, nodes: list[Node], depth: int, doc: Document, **kwargs
    ) -> list[Node]:
        def length_fn(node: Node):
            return self.tokenizer.length(node.content)

        groups: list[list[Node]] = aggregate_by_length(
            nodes, max_size=self.max_group_size, length_fn=length_fn
        )
        return_nodes: list[Node] = []
        for i, g in enumerate(groups):
            content = "".join(x.content for x in g)
            kwargs["depth"] = depth
            kwargs["subroutine"] = self.__class__.__name__
            kwargs["group"] = f"{i+1}/{len(groups)}"
            content = await summarize(passage=content, llm=self.llm, **kwargs)
            node = Node(
                content=content,
                document_id=doc.id,
                index=i,
                is_leaf=False,
                depth=depth,
                child_ids=[],
            )
            for nd in g:
                if node.child_ids is None:
                    node.child_ids = [nd.id]
                else:
                    node.child_ids.append(nd.id)
                nd.parent_id = node.id
            return_nodes.append(node)
            self._index[str(node.id)] = node
        return return_nodes

    @tracer.start_as_current_span("TreeIndex_abuild")
    async def abuild(self, doc: Document, **kwargs) -> list[Node]:
        logger.info(f"Building {self.__class__.__name__} on doc_id: {str(doc.id)}.")
        nodes = create_leaf_nodes(doc=doc, splitter=self.splitter)
        if not nodes:
            return []
        depth = 1
        max_iter = self.max_depth or len(nodes)
        prev_size = len(nodes)
        while len(nodes) > 1 and max_iter > 0:
            with tracer.start_as_current_span(f"process_nodes_depth_{depth}"):
                for node in nodes:
                    self._index[str(node.id)] = node
                nodes = await self._process_level(
                    nodes=nodes, depth=depth, doc=doc, **kwargs
                )
                depth += 1
                max_iter -= 1
                if len(nodes) >= prev_size:
                    logger.error(
                        "Failed to reduce nodes size ({prev_size} -> {prev_size})"
                    )
                    break
                prev_size == len(nodes)
        if not nodes:
            raise ValueError("Somehow we reduced past a single node!")
        doc.index_type = self.type
        doc.text_splitter = self.splitter.name
        doc.max_chunk_size = self.splitter.max_chunk_size
        doc.chunk_overlap = self.splitter.chunk_overlap
        r = list(self._index.values())
        self._index = {}  # TODO (Jonny): trying to make this stateless!
        return r

    def build(self, doc: Document, **kwargs) -> list[Node]:
        return asyncio.get_event_loop().run_until_complete(
            self.abuild(doc=doc, **kwargs)
        )


class TreeIndexWithContext(TreeIndex):
    type = IndexType.tree

    def __init__(
        self,
        tokenizer: Tokenizer,
        splitter: TextSplitter,
        llm: LLM,
        max_group_size: int | str = "auto",
        max_depth: int | None = None,
    ):
        self.tokenizer = tokenizer
        self.splitter = splitter
        self.llm = llm
        self._index: dict[str, Node] = {}
        self._tokens_processed = 0
        self.max_depth = max_depth

        prompt = templates.Summarize.render(passage="", llm=MockLLM(""))
        self._prompt_len = self.tokenizer.length(prompt)
        if isinstance(max_group_size, str):
            if max_group_size != "auto":
                raise ValueError("Max group size should be an int or auto.")
            max_group_size = auto_chunk_size_summarize(llm=llm)
        self.max_group_size = max_group_size

    @property
    def num_nodes(self):
        return len(self._index)

    @property
    def tokens_processed(self):
        return self._tokens_processed

    def estimate_llm_tokens(
        self, doc: Document, max_tokens: int = 512
    ) -> TokenEstimate:
        estimate = super().estimate_llm_tokens(doc=doc, max_tokens=max_tokens)
        # add the additional prompt input for the context
        llm_call_tokens = estimate.llm_call_tokens
        for row in estimate.metadata["layers"]:
            if row["depth"] > 0:
                llm_call_tokens += max_tokens * row["nodes"]
        return TokenEstimate(
            doc_tokens=estimate.doc_tokens,
            llm_call_tokens=llm_call_tokens,
            max_depth=estimate.max_depth,
            metadata=estimate.metadata,
        )

    @tracer.start_as_current_span("_process_level")
    async def _process_level(
        self, nodes: list[Node], depth: int, doc: Document, **kwargs
    ) -> list[Node]:
        def length_fn(node: Node):
            return self.tokenizer.length(node.content)

        groups: list[list[Node]] = aggregate_by_length(
            nodes, max_size=self.max_group_size, length_fn=length_fn
        )
        return_nodes: list[Node] = []
        prev_summary: str | None = None
        for i, g in enumerate(groups):
            content = "".join(x.content for x in g)
            kwargs["depth"] = depth
            kwargs["subroutine"] = self.__class__.__name__
            kwargs["group"] = f"{i+1}/{len(groups)}"
            content = await summarize_with_context(
                passage=content, llm=self.llm, prev_summary=prev_summary, **kwargs
            )
            node = Node(
                content=content,
                document_id=doc.id,
                index=i,
                is_leaf=False,
                depth=depth,
                child_ids=[],
            )
            for nd in g:
                if node.child_ids is None:
                    node.child_ids = [nd.id]
                else:
                    node.child_ids.append(nd.id)
                nd.parent_id = node.id
            return_nodes.append(node)
            self._index[str(node.id)] = node
            prev_summary = content
        return return_nodes

    @tracer.start_as_current_span("TreeIndexWithContext_abuild")
    async def abuild(self, doc: Document, **kwargs) -> list[Node]:
        logger.info(f"Building {self.__class__.__name__} on doc_id: {str(doc.id)}.")
        nodes = create_leaf_nodes(doc=doc, splitter=self.splitter)
        if not nodes:
            return []
        depth = 1
        max_iter = self.max_depth or len(nodes)
        prev_size = len(nodes)
        while len(nodes) > 1 and max_iter > 0:
            with tracer.start_as_current_span(f"process_nodes_depth_{depth}"):
                for node in nodes:
                    self._index[str(node.id)] = node
                nodes = await self._process_level(
                    nodes=nodes, depth=depth, doc=doc, **kwargs
                )
                depth += 1
                max_iter -= 1
                if len(nodes) >= prev_size:
                    logger.error(
                        "Failed to reduce nodes size ({prev_size} -> {prev_size})"
                    )
                    break
                prev_size == len(nodes)
        if not nodes:
            raise ValueError("Somehow we reduced past a single node!")
        doc.index_type = self.type
        doc.text_splitter = self.splitter.name
        doc.max_chunk_size = self.splitter.max_chunk_size
        doc.chunk_overlap = self.splitter.chunk_overlap
        r = list(self._index.values())
        self._index = {}  # TODO (Jonny): trying to make this stateless!
        return r

    def build(self, doc: Document, **kwargs) -> list[Node]:
        return asyncio.get_event_loop().run_until_complete(
            self.abuild(doc=doc, **kwargs)
        )
