import jinja2

env = jinja2.Environment(
    enable_async=False, autoescape=False, undefined=jinja2.StrictUndefined
)
