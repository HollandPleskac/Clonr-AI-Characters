# import os
# import pytest


# def is_docker() -> bool:
#     path = "/proc/self/cgroup"
#     if os.path.exists("/.dockerenv"):
#         return True
#     if os.path.isfile(path) and any("docker" in line for line in open(path)):
#         return True
#     return False


# IS_IN_DOCKER = is_docker()

# if not IS_IN_DOCKER:
#     os.environ["POSTGRES_HOST"] = "localhost"
#     os.environ["GRPC_EMBEDDING_HOST"] = "localhost"
#     os.environ["REDIS_HOST"] = "localhost"
