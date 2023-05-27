import uuid
from hashlib import sha256
from typing import Optional


def _validate_is_flat_dict(metadata_dict: dict) -> dict:
    """
    Validate that metadata dict is flat,
    and key is str, and value is one of (str, int, float).
    """
    if metadata_dict is not None:
        for key, val in metadata_dict.items():
            if not isinstance(key, str):
                raise ValueError("Metadata key must be str!")
            if not isinstance(val, (str, int, float)):
                raise ValueError("Value must be one of (str, int, float)")
    return metadata_dict or {}


class Document:
    def __init__(
        self,
        content: str,
        embedding: Optional[list[float]] = None,
        doc_id: Optional[str] = None,
        doc_hash: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        self.content = content
        self.embedding = embedding
        self.doc_id = doc_id or str(uuid.uuid4())
        self.metadata = _validate_is_flat_dict(metadata)

        self.doc_hash = doc_hash or self._generate_doc_hash()

    def _generate_doc_hash(self) -> str:
        """Generate a hash to represent the document."""
        doc_identity = str(self.content) + str(self.metadata)
        return sha256(doc_identity.encode("utf-8", "surrogatepass")).hexdigest()

    def get_content(self) -> str:
        if self.content is None:
            raise ValueError("text field not set.")
        return self.content

    def get_doc_id(self) -> str:
        if self.doc_id is None:
            raise ValueError("doc_id not set.")
        return self.doc_id

    def get_doc_hash(self) -> str:
        """Get doc_hash."""
        if self.doc_hash is None:
            raise ValueError("doc_hash is not set.")
        return self.doc_hash

    def get_embedding(self) -> list[float]:
        if self.embedding is None:
            raise ValueError("embedding not set.")
        return self.embedding

    @property
    def get_metadata_str(self) -> Optional[str]:
        """Extra info string."""
        if self.metadata is None:
            return None
        return "\n".join([f"{k}: {str(v)}" for k, v in self.extra_info.items()])

    @property
    def is_doc_id_none(self) -> bool:
        return self.doc_id is None

    @property
    def is_content_none(self) -> bool:
        """Check if text is None."""
        return self.content is None
