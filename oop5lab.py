import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Sequence, Generic, TypeVar, Dict, List


# Модель данных пользователя
@dataclass(order=True)
class Account:
    identifier: int = field(metadata={'alias': 'id'})
    username: str
    display_name: str
    credential: str = field(repr=False)
    contact_email: Optional[str] = None
    location: Optional[str] = None

    def __post_init__(self):
        self.sort_key = self.display_name.lower()

    def to_serializable(self) -> Dict:
        return {
            'id': self.identifier,
            'name': self.display_name,
            'login': self.username,
            'email': self.contact_email,
            'address': self.location
        }


# Обобщенный интерфейс репозитория
T = TypeVar('T')


class StorageInterface(ABC, Generic[T]):
    @abstractmethod
    def fetch_all(self) -> Sequence[T]:
        pass

    @abstractmethod
    def fetch_by_id(self, entity_id: int) -> Optional[T]:
        pass

    @abstractmethod
    def insert(self, entity: T) -> None:
        pass

    @abstractmethod
    def modify(self, entity: T) -> None:
        pass

    @abstractmethod
    def remove(self, entity: T) -> None:
        pass


# Специализированный интерфейс для пользователей
class AccountStorage(StorageInterface[Account], ABC):
    @abstractmethod
    def fetch_by_username(self, username: str) -> Optional[Account]:
        pass


# JSON-реализация хранилища
class JsonRepository(StorageInterface[T]):
    def __init__(self, storage_path: str):
        self._storage_path = storage_path
        self._entities: List[T] = self._load_data()

    def _load_data(self) -> List[T]:
        if not os.path.exists(self._storage_path):
            return []

        with open(self._storage_path, 'r', encoding='utf-8') as file:
            return [self._deserialize(item) for item in json.load(file)]

    def _save_data(self) -> None:
        with open(self._storage_path, 'w', encoding='utf-8') as file:
            json.dump([self._serialize(entity) for entity in self._entities], file)

    @abstractmethod
    def _serialize(self, entity: T) -> Dict:
        pass

    @abstractmethod
    def _deserialize(self, data: Dict) -> T:
        pass

    def fetch_all(self) -> Sequence[T]:
        return self._entities.copy()

    def fetch_by_id(self, entity_id: int) -> Optional[T]:
        return next((e for e in self._entities if getattr(e, 'identifier') == entity_id), None)

    def insert(self, entity: T) -> None:
        self._entities.append(entity)
        self._save_data()

    def modify(self, entity: T) -> None:
        for i, existing in enumerate(self._entities):
            if getattr(existing, 'identifier') == getattr(entity, 'identifier'):
                self._entities[i] = entity
                self._save_data()
                return

    def remove(self, entity: T) -> None:
        self._entities = [e for e in self._entities
                          if getattr(e, 'identifier') != getattr(entity, 'identifier')]
        self._save_data()


# Реализация хранилища аккаунтов
class AccountRepository(JsonRepository[Account], AccountStorage):
    def _serialize(self, account: Account) -> Dict:
        return {
            'id': account.identifier,
            'username': account.username,
            'name': account.display_name,
            'password': account.credential,
            'email': account.contact_email,
            'address': account.location
        }

    def _deserialize(self, data: Dict) -> Account:
        return Account(
            identifier=data['id'],
            username=data['username'],
            display_name=data['name'],
            credential=data['password'],
            contact_email=data.get('email'),
            location=data.get('address')
        )

    def fetch_by_username(self, username: str) -> Optional[Account]:
        return next((a for a in self._entities if a.username == username), None)


# Сервис аутентификации
class AuthManager:
    def __init__(self, session_path: str):
        self._session_path = session_path
        self._active_account: Optional[Account] = self._load_session()

    def _load_session(self) -> Optional[Account]:
        if not os.path.exists(self._session_path):
            return None

        with open(self._session_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return Account(
                identifier=data['id'],
                username=data['username'],
                display_name=data['name'],
                credential='',  # Пароль не сохраняется в сессии
                contact_email=data.get('email'),
                location=data.get('address')
            )

    def _save_session(self) -> None:
        if not self._active_account:
            if os.path.exists(self._session_path):
                os.remove(self._session_path)
            return

        with open(self._session_path, 'w', encoding='utf-8') as file:
            json.dump(self._active_account.to_serializable(), file)

    def authenticate(self, account: Account) -> None:
        self._active_account = account
        self._save_session()

    def terminate_session(self) -> None:
        self._active_account = None
        self._save_session()

    @property
    def has_active_session(self) -> bool:
        return self._active_account is not None

    @property
    def current_session(self) -> Optional[Account]:
        return self._active_account


def demonstrate_system():
    accounts_db = "accounts.json"
    session_db = "current_session.json"

    storage = AccountRepository(accounts_db)
    auth = AuthManager(session_db)

    print("\n=== Система управления аккаунтами ===")

    # Создание тестового аккаунта
    if not storage.fetch_by_username("test_user"):
        new_account = Account(
            identifier=1,
            username="test_user",
            display_name="Test User",
            credential="secure_password",
            contact_email="test@example.com"
        )
        storage.insert(new_account)
        print(f"Создан аккаунт: {new_account.display_name}")

    # Аутентификация
    account = storage.fetch_by_username("test_user")
    if account and account.credential == "secure_password":
        auth.authenticate(account)
        print(f"Аутентифицирован: {auth.current_session.display_name}")

    # Обновление данных
    if auth.has_active_session:
        account.display_name = "Updated Name"
        storage.modify(account)
        print(f"Обновлено имя: {account.display_name}")

    # Выход из системы
    auth.terminate_session()
    print("Сессия завершена")

    # Проверка автоаутентификации
    new_auth = AuthManager(session_db)
    if new_auth.has_active_session:
        print(f"Автоматическая аутентификация: {new_auth.current_session.display_name}")
    else:
        print("Нет активной сессии")


if __name__ == "__main__":
    demonstrate_system()