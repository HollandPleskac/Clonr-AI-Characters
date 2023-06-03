from app.modules.base import Module
from app.models import Memory


class MemoryModule(Module):
    async def connect(self):
        await super().connect()

    def add(self, memory, clone_id):
        memory_obj = Memory(memory=memory, clone_id=clone_id)
        self.session.add(memory_obj)
        self.session.commit()

    async def get(self, clone_id):
        memories = await self.session.get(Memory, clone_id)
        return memories
