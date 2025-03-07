'''
Just experimental persistence using a combination if in memory caching and
maybe some postgresql nosql columns
'''

'''
Ideally this would then be the only, or one of two, singletons in the entire app
depending on how final version of keeping loaded models in memory ends up being
'''
class PersistenceService():
    def __init__(self) -> None:
        pass