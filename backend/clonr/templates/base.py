from abc import ABC, abstractclassmethod

import jinja2

env = jinja2.Environment(
    enable_async=False, autoescape=False, undefined=jinja2.StrictUndefined
)


class Template(ABC):
    @abstractclassmethod
    def render(cls, *args, **kwargs) -> str:
        # TODO (Jonny): We should have a render_chat and render_instruct method,
        # Then at run time perform something like (if llm.chat_model return render_chat ...)
        pass
