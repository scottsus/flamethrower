from dependency_injector import containers, providers
from flamethrower.utils.token_counter import TokenCounter

class LMContainer(containers.DeclarativeContainer):
    token_counter = providers.Singleton(TokenCounter)

lm_container = LMContainer()
