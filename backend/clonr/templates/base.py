import jinja2
from abc import ABC, abstractclassmethod


env = jinja2.Environment(
    enable_async=False, autoescape=False, undefined=jinja2.StrictUndefined
)


class Template(ABC):
    @abstractclassmethod
    def render(cls, *args, **kwargs) -> str:
        pass

    @property
    @abstractclassmethod
    def template(cls):
        pass
