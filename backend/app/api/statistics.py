# TODO (Jonny): Everything on this route hits a redis cache
# we are doing passive compute, meaning for each route we should have some kind of
# redis cache wrapper that does something like
# (1) check redis for result (2) return if there (3) if not compute result (4) r.set(<result>, ex=<time-to-live>)
# This page should contain stats for both users and creators, and maybe for us, the admin?
# total number of messages, number of conversations, messages per conversation, top bots, costs ... idk other shit
