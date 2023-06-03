from app.modules.base import Module
from app.models import Motivation


class MotivationModule(Module):
    async def connect(self):
        await super().connect()

    def add(self, motivation, clone_id):
        motivation_obj = Motivation(motivation=motivation, clone_id=clone_id)
        self.session.add(motivation_obj)
        self.session.commit()

    async def get(self, clone_id):
        motivations = await self.session.get(Motivation, clone_id)
        return motivations
