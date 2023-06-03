from app.modules.base import Module
from app.models import Reflection


class ReflectionModule(Module):
    async def connect(self):
        await super().connect()

    def add(self, reflection, clone_id):
        reflection_obj = Reflection(reflection=reflection, clone_id=clone_id)
        self.session.add(reflection_obj)
        self.session.commit()

    async def get(self, clone_id):
        reflections = await self.session.get(Reflection, clone_id)
        return reflections
