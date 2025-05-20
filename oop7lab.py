import threading
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, TypeVar


class LifeStyle(Enum):
    PER_REQUEST = 1
    SCOPED = 2
    SINGLETON = 3


T = TypeVar("T")


class Injector:
    def __init__(self):
        self._registry: Dict[Type, Dict] = {}
        self._singletons: Dict[Type, Any] = {}
        self._scoped_instances: Dict[int, Dict[Type, Any]] = {}
        self._current_scope_id: Optional[int] = None
        self._next_scope_id = 0
        self._lock = threading.RLock()
        self._construction_stack: Set[Type] = set()

    def register(
        self,
        interface_type: Type[T],
        implementation=None,
        life_style: LifeStyle = LifeStyle.PER_REQUEST,
        params: Dict[str, Any] = None,
    ) -> None:
        is_factory = callable(implementation) and not isinstance(implementation, type)

        self._registry[interface_type] = {
            "implementation": implementation,
            "life_style": life_style,
            "params": params or {},
            "is_factory": is_factory,
        }

    def get_instance(self, interface_type: Type[T]) -> T:
        if interface_type not in self._registry:
            raise KeyError(f"Interface {interface_type.__name__} is not registered")

        registration = self._registry[interface_type]
        life_style = registration["life_style"]

        if interface_type in self._construction_stack:
            raise ValueError(
                f"Circular dependency detected when constructing {interface_type.__name__}"
            )

        if life_style == LifeStyle.SINGLETON:
            if interface_type not in self._singletons:
                self._construction_stack.add(interface_type)
                try:
                    self._singletons[interface_type] = self._create_instance(
                        interface_type
                    )
                finally:
                    self._construction_stack.remove(interface_type)
            return self._singletons[interface_type]

        elif life_style == LifeStyle.SCOPED:
            if self._current_scope_id is None:
                raise RuntimeError("No active scope")

            scope_instances = self._scoped_instances.get(self._current_scope_id, {})

            if interface_type not in scope_instances:
                self._construction_stack.add(interface_type)
                try:
                    instance = self._create_instance(interface_type)
                    scope_instances[interface_type] = instance
                    self._scoped_instances[self._current_scope_id] = scope_instances
                finally:
                    self._construction_stack.remove(interface_type)

            return scope_instances[interface_type]

        else:
            self._construction_stack.add(interface_type)
            try:
                return self._create_instance(interface_type)
            finally:
                self._construction_stack.remove(interface_type)

    def _create_instance(self, interface_type: Type[T]) -> T:
        registration = self._registry[interface_type]
        implementation = registration["implementation"]
        params = registration["params"].copy()
        is_factory = registration["is_factory"]

        if is_factory:
            return implementation(**params)
        else:
            constructor_params = {}

            import inspect

            if hasattr(implementation, "__init__"):
                sig = inspect.signature(implementation.__init__)

                for param_name, param in list(sig.parameters.items())[1:]:
                    param_type = param.annotation

                    if param_name in params:
                        constructor_params[param_name] = params[param_name]
                    elif param_type in self._registry:
                        constructor_params[param_name] = self.get_instance(param_type)
                    elif param.default is not inspect.Parameter.empty:
                        pass

            for param_name, value in params.items():
                if param_name not in constructor_params:
                    constructor_params[param_name] = value

            return implementation(**constructor_params)

    @contextmanager
    def scope(self):
        with self._lock:
            scope_id = self._next_scope_id
            self._next_scope_id += 1
            old_scope_id = self._current_scope_id
            self._current_scope_id = scope_id
            self._scoped_instances[scope_id] = {}

        try:
            yield
        finally:
            with self._lock:
                self._current_scope_id = old_scope_id
                if scope_id in self._scoped_instances:
                    del self._scoped_instances[scope_id]


class ILogger(ABC):
    @abstractmethod
    def log(self, message: str) -> None:
        pass


class IRepository(ABC):
    @abstractmethod
    def get_data(self) -> List[str]:
        pass


class IService(ABC):
    @abstractmethod
    def process(self) -> str:
        pass


class ConsoleLogger(ILogger):
    def log(self, message: str) -> None:
        print(f"DEBUG: {message}")


class FileLogger(ILogger):
    def __init__(self, file_path: str = "app.log"):
        self.file_path = file_path
        with open(self.file_path, "a") as f:
            f.write("------Logger initialized\n")

    def log(self, message: str) -> None:
        with open(self.file_path, "a") as f:
            f.write(f"INFO: {message}\n")


class InMemoryRepository(IRepository):
    def __init__(self, initial_data: List[str] = None):
        self.data = initial_data or ["Default data 1", "Default data 2"]

    def get_data(self) -> List[str]:
        return self.data


class DatabaseRepository(IRepository):
    def __init__(self, connection_string: str, logger: ILogger):
        self.connection_string = connection_string
        self.logger = logger
        self.logger.log(
            f"DatabaseRepository initialized with connection: {connection_string}"
        )

    def get_data(self) -> List[str]:
        self.logger.log("Fetching data from database")
        return [f"Data from DB: {i}" for i in range(1, 4)]


class BasicService(IService):
    def __init__(self, repository: IRepository, logger: ILogger):
        self.repository = repository
        self.logger = logger
        self.logger.log("BasicService initialized")

    def process(self) -> str:
        self.logger.log("Processing with BasicService")
        data = self.repository.get_data()
        return f"Processed {len(data)} items with BasicService"


class AdvancedService(IService):
    def __init__(self, repository: IRepository, logger: ILogger, prefix: str = "ADV"):
        self.repository = repository
        self.logger = logger
        self.prefix = prefix
        self.logger.log(f"AdvancedService initialized with prefix: {prefix}")

    def process(self) -> str:
        self.logger.log("Processing with AdvancedService")
        data = self.repository.get_data()
        return f"{self.prefix}: Processed {len(data)} items with enhanced algorithms"


def main():
    injector = Injector()

    injector.register(ILogger, ConsoleLogger, LifeStyle.SINGLETON)
    injector.register(
        IRepository,
        InMemoryRepository,
        LifeStyle.PER_REQUEST,
        {"initial_data": ["Debug Data A", "Debug Data B", "Debug Data C"]},
    )
    injector.register(IService, BasicService, LifeStyle.SCOPED)

    repo1 = injector.get_instance(IRepository)
    repo2 = injector.get_instance(IRepository)
    print(f"repo1 is repo2 = {repo1 is repo2}")

    logger1 = injector.get_instance(ILogger)
    logger2 = injector.get_instance(ILogger)
    print(f"logger1 is logger2 = {logger1 is logger2}")

    with injector.scope():
        service1 = injector.get_instance(IService)
        service2 = injector.get_instance(IService)
        print(f"service1 is service2 = {service1 is service2}")
        print(f"Result: {service1.process()}")

    with injector.scope():
        service3 = injector.get_instance(IService)
        print(f"service1 is service3 = {service1 is service3}")
        print(f"Result: {service3.process()}")


if __name__ == "__main__":
    main()