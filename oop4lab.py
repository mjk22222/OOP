from abc import ABC, abstractmethod
from typing import List, TypeVar, Any

# Объявление типа для аннотаций
T = TypeVar('T')


# Интерфейсы для системы наблюдения
class IPropertyObserver(ABC):
    @abstractmethod
    def property_updated(self, source: Any, prop_name: str) -> None:
        """Вызывается после изменения свойства"""
        pass


class IPropertyValidator(ABC):
    @abstractmethod
    def validate_change(self, source: Any, prop_name: str, old_val: T, new_val: T) -> bool:
        """Проверяет допустимость изменения свойства"""
        pass


# Интерфейсы для наблюдаемых объектов
class IObservableProperties(ABC):
    @abstractmethod
    def subscribe_observer(self, observer: IPropertyObserver) -> None:
        """Добавляет наблюдателя изменений"""
        pass

    @abstractmethod
    def unsubscribe_observer(self, observer: IPropertyObserver) -> None:
        """Удаляет наблюдателя изменений"""
        pass


class IValidatableProperties(ABC):
    @abstractmethod
    def subscribe_validator(self, validator: IPropertyValidator) -> None:
        """Добавляет валидатор изменений"""
        pass

    @abstractmethod
    def unsubscribe_validator(self, validator: IPropertyValidator) -> None:
        """Удаляет валидатор изменений"""
        pass


# Реализация класса с наблюдаемыми свойствами
class Person(IObservableProperties, IValidatableProperties):
    def __init__(self, full_name: str, years: int):
        self._full_name = full_name
        self._years = years
        self._observers: List[IPropertyObserver] = []
        self._validators: List[IPropertyValidator] = []

    # Реализация интерфейса IObservableProperties
    def subscribe_observer(self, observer: IPropertyObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def unsubscribe_observer(self, observer: IPropertyObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    # Реализация интерфейса IValidatableProperties
    def subscribe_validator(self, validator: IPropertyValidator) -> None:
        if validator not in self._validators:
            self._validators.append(validator)

    def unsubscribe_validator(self, validator: IPropertyValidator) -> None:
        if validator in self._validators:
            self._validators.remove(validator)

    # Свойства с валидацией и уведомлением
    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, new_name: str) -> None:
        if new_name == self._full_name:
            return

        # Валидация изменения
        if self._validators:
            validation_passed = all(
                v.validate_change(self, "full_name", self._full_name, new_name)
                for v in self._validators
            )
            if not validation_passed:
                return

        old_name = self._full_name
        self._full_name = new_name

        # Уведомление наблюдателей
        for observer in self._observers:
            observer.property_updated(self, "full_name")

    @property
    def years(self) -> int:
        return self._years

    @years.setter
    def years(self, new_age: Any) -> None:
        try:
            new_age = int(new_age)
        except (ValueError, TypeError):
            print("Ошибка: возраст должен быть числом")
            return

        if new_age == self._years:
            return

        # Валидация изменения
        if self._validators:
            validation_passed = all(
                v.validate_change(self, "years", self._years, new_age)
                for v in self._validators
            )
            if not validation_passed:
                return

        old_age = self._years
        self._years = new_age

        # Уведомление наблюдателей
        for observer in self._observers:
            observer.property_updated(self, "years")


# Реализации наблюдателей и валидаторов
class ChangeLogger(IPropertyObserver):
    def property_updated(self, source: Any, prop_name: str) -> None:
        print(f"[Изменение] Свойство '{prop_name}' объекта {source.__class__.__name__} "
              f"изменено на: {getattr(source, prop_name)}")


class AgeValidator(IPropertyValidator):
    def validate_change(self, source: Any, prop_name: str, old_val: int, new_val: int) -> bool:
        if prop_name == "years":
            if new_val < 0:
                print("Ошибка: возраст не может быть отрицательным")
                return False
            if new_val > 120:
                print("Ошибка: возраст не может быть больше 120 лет")
                return False
        return True


class NameValidator(IPropertyValidator):
    def validate_change(self, source: Any, prop_name: str, old_val: str, new_val: str) -> bool:
        if prop_name == "full_name":
            if len(new_val.strip()) < 2:
                print("Ошибка: имя должно содержать минимум 2 символа")
                return False
            if not new_val.replace(" ", "").isalpha():
                print("Ошибка: имя должно содержать только буквы и пробелы")
                return False
        return True


# Демонстрация работы
def demonstrate_property_system():
    # Создаем объект
    person = Person("Иван Петров", 30)

    # Создаем и подписываем наблюдателей и валидаторов
    logger = ChangeLogger()
    person.subscribe_observer(logger)

    age_checker = AgeValidator()
    name_checker = NameValidator()
    person.subscribe_validator(age_checker)
    person.subscribe_validator(name_checker)

    print("=== Корректные изменения ===")
    person.full_name = "Алексей Смирнов"
    person.years = 35

    print("\n=== Некорректные изменения ===")
    person.full_name = "А1"  # Недопустимое имя
    person.full_name = "О"  # Слишком короткое имя
    person.years = -5  # Отрицательный возраст
    person.years = 150  # Слишком большой возраст

    print("\n=== Финальные значения ===")
    print(f"Имя: {person.full_name}, Возраст: {person.years}")


if __name__ == "__main__":
    demonstrate_property_system()