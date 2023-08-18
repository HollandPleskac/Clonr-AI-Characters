from abc import ABC

import jinja2

env = jinja2.Environment(
    enable_async=False, autoescape=False, undefined=jinja2.StrictUndefined
)


class Template(ABC):
    pass
    # @abstractclassmethod
    # def render(cls, *args: Any, **kwargs: Any) -> str:
    #     raise NotImplementedError()
