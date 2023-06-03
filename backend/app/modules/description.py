from app.modules.base import Module
from app.models import Description


class DescriptionModule(Module):
    async def connect(self):
        await super().connect()

    def add(self, description, clone_id):
        description_obj = Description(description=description, clone_id=clone_id)
        self.session.add(description_obj)
        self.session.commit()

    async def get(self, clone_id):
        descriptions = await self.session.get(Description, clone_id)
        return descriptions
