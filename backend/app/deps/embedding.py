from app.embedding import EmbeddingClient


async def get_embedding_client():
    async with EmbeddingClient() as client:
        yield client
