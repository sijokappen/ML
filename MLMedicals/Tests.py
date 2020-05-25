from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional


class Handler(ABC):
    """
    The Handler interface declares a method for building the chain of handlers.
    It also declares a method for executing a request.
    """

    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    def handle(self, request) -> Optional[str]:
        pass


class AbstractTest(Handler):
    """
    The default chaining behavior can be implemented inside a base handler
    class.
    """

    _next_handler: Handler = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        # Returning a handler from here will let us link handlers in a
        # convenient way like this:
        # monkey.set_next(squirrel).set_next(dog)
        return handler

    @abstractmethod
    def handle(self, request: Any) -> str:
        if self._next_handler:
            return self._next_handler.handle(request)

        return None


"""
All Concrete Handlers either handle a request or pass it to the next handler in
the chain.
"""


class Test1(AbstractTest):
    def handle(self, request: Any) -> str:
        print("Test1 ")
        return super().handle(request)


class Test2(AbstractTest):
    def handle(self, request: Any) -> str:
        print("Test2 ")
        return super().handle(request)


class Test3(AbstractTest):
    def handle(self, request: Any) -> str:
        print("Test3 ")
        return super().handle(request)

class Test4(AbstractTest):
    def handle(self, request: Any) -> str:
        print("Test4 ")
        return super().handle(request)


def client_code(handler: Handler) -> None:
    """
    The client code is usually suited to work with a single handler. In most
    cases, it is not even aware that the handler is part of a chain.
    """

    result = handler.handle("Name")
    if result:
    	print(f"  {result}", end="")


if __name__ == "__main__":
    testOne = Test1()
    testTwo = Test2()
    testThree = Test3()
    testFour = Test4()

    testOne.set_next(testTwo).set_next(testThree).set_next(testFour)

    # The client should be able to send a request to any handler, not just the
    # first one in the chain.
    client_code(testOne)

