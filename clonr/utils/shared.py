import weakref
from functools import lru_cache, wraps


def instance_level_lru_cache(maxsize: int | None = None, typed: bool = False):
    """LRU Cache decorator that keeps a weak reference to "self"
    to be used for decorating class methods. It disappears when the class instance disappears.
    Source:
    https://stackoverflow.com/questions/33672412/python-functools-lru-cache-with-instance-methods-release-object

    Args:
        maxsize (int, optional): max cache size. Defaults to None.
        typed (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """

    def wrapper(func):
        @lru_cache(maxsize, typed)
        def _func(_self, *args, **kwargs):
            return func(_self(), *args, **kwargs)

        @wraps(func)
        def inner(self, *args, **kwargs):
            return _func(weakref.ref(self), *args, **kwargs)

        return inner

    return wrapper
