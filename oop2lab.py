from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class TextColor(Enum):
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    DEFAULT = '\033[0m'


@dataclass
class SymbolPatterns:
    patterns: Dict[str, List[str]]

    @classmethod
    def from_file(cls, filename: str) -> 'SymbolPatterns':
        char_patterns = {}
        current_char = None

        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line.endswith(':'):
                    current_char = line[:-1]
                    char_patterns[current_char] = []
                elif current_char is not None and line:
                    char_patterns[current_char].append(line)

        return cls(char_patterns)

    def get_pattern(self, character: str) -> List[str]:
        return self.patterns.get(character.upper(), [])


class ConsoleArtPrinter:
    def __init__(self,
                 color: TextColor = TextColor.DEFAULT,
                 start_pos: Tuple[int, int] = (1, 1),
                 fill_char: str = '*',
                 font: SymbolPatterns = None):
        self.color = color
        self.position = start_pos
        self.fill_char = fill_char
        self.font = font

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(TextColor.DEFAULT.value, end='')

    def render_text(self, message: str) -> None:
        base_y, base_x = self.position

        for line_num in range(5):
            output_line = []

            for char in message:
                char_lines = self.font.get_pattern(char)
                if line_num < len(char_lines):
                    rendered_line = char_lines[line_num].replace('*', self.fill_char)
                    output_line.append(rendered_line)

            if output_line:
                combined_line = '  '.join(output_line)
                print(f"\033[{base_y + line_num};{base_x}H{self.color.value}{combined_line}")

    @classmethod
    def quick_print(cls,
                    text: str,
                    color: TextColor,
                    position: Tuple[int, int],
                    symbol: str,
                    font_data: SymbolPatterns):
        with cls(color, position, symbol, font_data) as printer:
            printer.render_text(text)


if __name__ == "__main__":
    font_data = SymbolPatterns.from_file("letters.txt")

    ConsoleArtPrinter.quick_print("WB", TextColor.BLUE, (5, 5), "*", font_data)

    with ConsoleArtPrinter(TextColor.CYAN, (10, 10), "№", font_data) as artist:
        artist.render_text("HE")
