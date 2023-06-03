from app.modules.base import Module
from app.models import ExampleDialogue


class ExampleDialogueModule(Module):
    async def connect(self):
        await super().connect()

    def add(self, example_dialogue, clone_id):
        example_dialogue_obj = ExampleDialogue(
            example_dialogue=example_dialogue, clone_id=clone_id
        )
        self.session.add(example_dialogue_obj)
        self.session.commit()

    async def get(self, clone_id):
        example_dialogues = await self.session.get(ExampleDialogue, clone_id)
        return example_dialogues
