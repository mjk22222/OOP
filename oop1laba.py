from math import sqrt
from typing import Tuple, Iterator

# Константы экрана
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080


class ScreenPoint:
    """Класс для представления точки на экране с проверкой границ"""

    def __init__(self, x: int, y: int):
        self._x = self._validate_coordinate(x, SCREEN_WIDTH, 'x')
        self._y = self._validate_coordinate(y, SCREEN_HEIGHT, 'y')

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int) -> None:
        self._x = self._validate_coordinate(value, SCREEN_WIDTH, 'x')

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int) -> None:
        self._y = self._validate_coordinate(value, SCREEN_HEIGHT, 'y')

    @staticmethod
    def _validate_coordinate(value: int, max_value: int, coord_name: str) -> int:
        """Проверяет корректность координаты"""
        if not isinstance(value, int):
            raise TypeError(f"{coord_name} coordinate must be integer")
        if not 0 <= value <= max_value:
            raise ValueError(f"{coord_name} coordinate must be between 0 and {max_value}")
        return value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ScreenPoint):
            return False
        return self._x == other.x and self._y == other.y

    def __str__(self) -> str:
        return f"Point(x={self._x}, y={self._y})"

    def __repr__(self) -> str:
        return f"ScreenPoint({self._x}, {self._y})"


class ScreenVector:
    """Класс для работы с 2D векторами на экране"""

    def __init__(self, dx: int = None, dy: int = None,
                 start: ScreenPoint = None, end: ScreenPoint = None):
        if start is not None and end is not None:
            self._dx = end.x - start.x
            self._dy = end.y - start.y
        elif dx is not None and dy is not None:
            self._dx = dx
            self._dy = dy
        else:
            raise ValueError("Vector must be initialized with either (dx, dy) or (start, end)")

    @property
    def dx(self) -> int:
        return self._dx

    @property
    def dy(self) -> int:
        return self._dy

    def __getitem__(self, index: int) -> int:
        if index == 0:
            return self._dx
        elif index == 1:
            return self._dy
        raise IndexError("Vector index out of range (0-1)")

    def __setitem__(self, index: int, value: int) -> None:
        if index == 0:
            self._dx = value
        elif index == 1:
            self._dy = value
        else:
            raise IndexError("Vector index out of range (0-1)")

    def __iter__(self) -> Iterator[int]:
        yield self._dx
        yield self._dy

    def __len__(self) -> int:
        return 2

    def magnitude(self) -> float:
        """Возвращает длину вектора"""
        return sqrt(self._dx ** 2 + self._dy ** 2)

    def __abs__(self) -> float:
        return self.magnitude()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ScreenVector):
            return False
        return self._dx == other.dx and self._dy == other.dy

    def __str__(self) -> str:
        return f"Vector(dx={self._dx}, dy={self._dy})"

    def __repr__(self) -> str:
        return f"ScreenVector({self._dx}, {self._dy})"

    # Арифметические операции
    def __add__(self, other: 'ScreenVector') -> 'ScreenVector':
        if not isinstance(other, ScreenVector):
            raise TypeError("Can only add ScreenVector to another ScreenVector")
        return ScreenVector(dx=self._dx + other.dx, dy=self._dy + other.dy)

    def __sub__(self, other: 'ScreenVector') -> 'ScreenVector':
        if not isinstance(other, ScreenVector):
            raise TypeError("Can only subtract ScreenVector from another ScreenVector")
        return ScreenVector(dx=self._dx - other.dx, dy=self._dy - other.dy)

    def __mul__(self, scalar: int) -> 'ScreenVector':
        if not isinstance(scalar, (int, float)):
            raise TypeError("Can only multiply by scalar (int or float)")
        return ScreenVector(dx=self._dx * scalar, dy=self._dy * scalar)

    def __truediv__(self, scalar: int) -> 'ScreenVector':
        if not isinstance(scalar, (int, float)):
            raise TypeError("Can only divide by scalar (int or float)")
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return ScreenVector(dx=self._dx / scalar, dy=self._dy / scalar)

    # Векторные операции
    def dot_product(self, other: 'ScreenVector') -> int:
        """Скалярное произведение векторов"""
        return self._dx * other.dx + self._dy * other.dy

    @classmethod
    def dot(cls, v1: 'ScreenVector', v2: 'ScreenVector') -> int:
        """Статический метод скалярного произведения"""
        return v1.dot_product(v2)

    def cross_product(self, other: 'ScreenVector') -> int:
        """Векторное произведение векторов (псевдоскаляр)"""
        return self._dx * other.dy - self._dy * other.dx

    @classmethod
    def cross(cls, v1: 'ScreenVector', v2: 'ScreenVector') -> int:
        """Статический метод векторного произведения"""
        return v1.cross_product(v2)

    @classmethod
    def triple_product(cls, v1: 'ScreenVector', v2: 'ScreenVector', v3: 'ScreenVector') -> int:
        """Смешанное произведение трех векторов"""
        return v1.cross_product(v2) * v3.dx + v1.cross_product(v2) * v3.dy


def demonstrate_vector_operations():
    """Демонстрация работы с векторами"""
    print("=== Создание точек ===")
    p1 = ScreenPoint(100, 200)
    p2 = ScreenPoint(150, 250)
    p3 = ScreenPoint(200, 300)

    print(f"Точка 1: {p1}")
    print(f"Точка 2: {p2}")
    print(f"Точка 3: {p3}")

    print("\n=== Создание векторов ===")
    v1 = ScreenVector(start=p1, end=p2)
    v2 = ScreenVector(start=p2, end=p3)
    v3 = ScreenVector(dx=50, dy=50)

    print(f"Вектор 1 (из точек): {v1}")
    print(f"Вектор 2 (из точек): {v2}")
    print(f"Вектор 3 (из компонентов): {v3}")

    print("\n=== Доступ к компонентам ===")
    print(f"v1[0] = {v1[0]}, v1[1] = {v1[1]}")
    print("Итерация по компонентам вектора:")
    for component in v1:
        print(component)

    print("\n=== Арифметические операции ===")
    print(f"Сумма векторов: {v1 + v2}")
    print(f"Разность векторов: {v1 - v2}")
    print(f"Умножение на скаляр: {v1 * 2}")
    print(f"Деление на скаляр: {v1 / 2}")

    print("\n=== Векторные операции ===")
    print(f"Длина вектора v1: {v1.magnitude()}")
    print(f"Скалярное произведение: {v1.dot_product(v2)}")
    print(f"Векторное произведение: {v1.cross_product(v2)}")
    print(f"Смешанное произведение: {ScreenVector.triple_product(v1, v2, v3)}")


if __name__ == "__main__":
    demonstrate_vector_operations()