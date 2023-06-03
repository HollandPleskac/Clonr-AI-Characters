from app.modules.base import Module
from app.models import Fact


class FactModule(Module):
    async def connect(self):
        await super().connect()

    def add(self, fact, clone_id):
        fact_obj = Fact(fact=fact, clone_id=clone_id)
        self.session.add(fact_obj)
        self.session.commit()

    async def get(self, clone_id):
        facts = await self.session.get(Fact, clone_id)
        return facts
