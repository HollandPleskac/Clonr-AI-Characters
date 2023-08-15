from abc import ABC, abstractclassmethod

import jinja2

env = jinja2.Environment(
    enable_async=False, autoescape=False, undefined=jinja2.StrictUndefined
)


class Template(ABC):
    @abstractclassmethod
    def render(cls, *args, **kwargs) -> str:
        raise NotImplementedError()
