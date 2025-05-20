import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AppState:
    current_text: str = ""
    sound_level: int = 50
    is_player_running: bool = False
    output_history: List[str] = field(default_factory=list)

    def record_output(self, message: str):
        self.output_history.append(message)
        print(f"CONSOLE: {message}")
        with open("keyboard_output.txt", "a") as file:
            file.write(f"{message}\n")


class Command(ABC):
    @abstractmethod
    def execute(self, state: AppState) -> None:
        pass

    @abstractmethod
    def undo(self, state: AppState) -> None:
        pass

    @abstractmethod
    def redo(self, state: AppState) -> None:
        pass

    @abstractmethod
    def to_dict(self) -> Dict:
        pass


class TextInputCommand(Command):
    def __init__(self, character: str):
        self.character = character
        self._prev_state = ""

    def execute(self, state: AppState) -> None:
        self._prev_state = state.current_text
        state.current_text += self.character
        state.record_output(state.current_text)

    def undo(self, state: AppState) -> None:
        state.current_text = self._prev_state
        state.record_output(state.current_text)

    def redo(self, state: AppState) -> None:
        state.current_text += self.character
        state.record_output(state.current_text)

    def to_dict(self) -> Dict:
        return {"command_type": "text_input", "character": self.character}


class AdjustVolumeCommand(Command):
    def __init__(self, adjustment: int):
        self.adjustment = adjustment
        self._prev_level = 50

    def execute(self, state: AppState) -> None:
        self._prev_level = state.sound_level
        state.sound_level = max(0, min(100, state.sound_level + self.adjustment))
        state.record_output(f"Volume changed to {state.sound_level}%")

    def undo(self, state: AppState) -> None:
        state.sound_level = self._prev_level
        state.record_output(f"Volume restored to {state.sound_level}%")

    def redo(self, state: AppState) -> None:
        state.sound_level = max(0, min(100, self._prev_level + self.adjustment))
        state.record_output(f"Volume changed to {state.sound_level}%")

    def to_dict(self) -> Dict:
        return {"command_type": "adjust_volume", "adjustment": self.adjustment}


class TogglePlayerCommand(Command):
    def __init__(self):
        self._prev_state = False

    def execute(self, state: AppState) -> None:
        self._prev_state = state.is_player_running
        state.is_player_running = not state.is_player_running
        action = "started" if state.is_player_running else "stopped"
        state.record_output(f"Media player {action}")

    def undo(self, state: AppState) -> None:
        state.is_player_running = self._prev_state
        action = "started" if self._prev_state else "stopped"
        state.record_output(f"Media player {action}")

    def redo(self, state: AppState) -> None:
        state.is_player_running = not self._prev_state
        action = "started" if not self._prev_state else "stopped"
        state.record_output(f"Media player {action}")

    def to_dict(self) -> Dict:
        return {"command_type": "toggle_player"}


class HistoryCommand(Command):
    def __init__(self, keyboard: 'VirtualKeyboard', is_undo: bool):
        self.keyboard = keyboard
        self.is_undo = is_undo

    def execute(self, state: AppState) -> None:
        if self.is_undo:
            self.keyboard.undo_last_command()
        else:
            self.keyboard.redo_last_command()

    def undo(self, state: AppState) -> None:
        pass

    def redo(self, state: AppState) -> None:
        pass

    def to_dict(self) -> Dict:
        return {"command_type": "undo" if self.is_undo else "redo"}


class VirtualKeyboard:
    def __init__(self):
        self.state = AppState()
        self.key_mappings: Dict[str, Command] = {}
        self.command_history: List[Command] = []
        self.undo_stack: List[Command] = []

    def map_key(self, key_combination: str, command: Command) -> None:
        self.key_mappings[key_combination] = command

    def press_key(self, key_combination: str) -> None:
        if key_combination in self.key_mappings:
            command = self.key_mappings[key_combination]
            command.execute(self.state)
            if not isinstance(command, HistoryCommand):
                self.command_history.append(command)
                self.undo_stack.clear()

    def undo_last_command(self) -> None:
        if self.command_history:
            command = self.command_history.pop()
            command.undo(self.state)
            self.undo_stack.append(command)

    def redo_last_command(self) -> None:
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.redo(self.state)
            self.command_history.append(command)

    def save_mappings(self, filename: str = "keyboard_mappings.json") -> None:
        mappings = {
            key: cmd.to_dict()
            for key, cmd in self.key_mappings.items()
        }
        with open(filename, "w") as file:
            json.dump(mappings, file, indent=2)

    def load_mappings(self, filename: str = "keyboard_mappings.json") -> None:
        try:
            with open(filename, "r") as file:
                mappings = json.load(file)

            for key, cmd_data in mappings.items():
                cmd_type = cmd_data["command_type"]
                if cmd_type == "text_input":
                    self.key_mappings[key] = TextInputCommand(cmd_data["character"])
                elif cmd_type == "adjust_volume":
                    self.key_mappings[key] = AdjustVolumeCommand(cmd_data["adjustment"])
                elif cmd_type == "toggle_player":
                    self.key_mappings[key] = TogglePlayerCommand()
                elif cmd_type in ("undo", "redo"):
                    self.key_mappings[key] = HistoryCommand(self, cmd_type == "undo")
        except FileNotFoundError:
            pass


def initialize_keyboard() -> VirtualKeyboard:
    keyboard = VirtualKeyboard()

    # Настройка стандартных привязок клавиш
    keyboard.map_key("a", TextInputCommand("a"))
    keyboard.map_key("b", TextInputCommand("b"))
    keyboard.map_key("c", TextInputCommand("c"))
    keyboard.map_key("d", TextInputCommand("d"))
    keyboard.map_key("vol_up", AdjustVolumeCommand(10))
    keyboard.map_key("vol_down", AdjustVolumeCommand(-10))
    keyboard.map_key("media", TogglePlayerCommand())
    keyboard.map_key("undo", HistoryCommand(keyboard, True))
    keyboard.map_key("redo", HistoryCommand(keyboard, False))

    return keyboard


def demonstrate_keyboard():
    # Очистка файла вывода перед началом
    open("keyboard_output.txt", "w").close()

    keyboard = initialize_keyboard()
    keyboard.load_mappings()

    # Последовательность тестовых команд
    test_sequence = [
        "a", "b", "c",  # Ввод текста
        "undo", "undo",  # Отмена действий
        "redo",  # Повтор действия
        "vol_up",  # Увеличение громкости
        "vol_down",  # Уменьшение громкости
        "media",  # Запуск/остановка плеера
        "d",  # Ввод текста
        "undo", "undo"  # Отмена действий
    ]

    for key in test_sequence:
        keyboard.press_key(key)

    keyboard.save_mappings()


if __name__ == "__main__":
    demonstrate_keyboard()