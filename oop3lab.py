import re
from abc import ABC, abstractmethod
from typing import List
from datetime import datetime


class ILogCondition(ABC):
    @abstractmethod
    def is_satisfied(self, log_entry: str) -> bool:
        pass


class ILogDestination(ABC):
    @abstractmethod
    def send_log(self, log_entry: str) -> None:
        pass


class TextMatchCondition(ILogCondition):
    def __init__(self, search_text: str):
        self.search_text = search_text

    def is_satisfied(self, log_entry: str) -> bool:
        return self.search_text.lower() in log_entry.lower()


class RegexCondition(ILogCondition):
    def __init__(self, pattern: str):
        self.regex = re.compile(pattern)

    def is_satisfied(self, log_entry: str) -> bool:
        return bool(self.regex.search(log_entry))


class TerminalOutput(ILogDestination):
    def send_log(self, log_entry: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] TERMINAL: {log_entry}")


class FileStorage(ILogDestination):
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def send_log(self, log_entry: str) -> None:
        with open(self.storage_path, 'a', encoding='utf-8') as log_file:
            timestamp = datetime.now().isoformat()
            log_file.write(f"{timestamp}|{log_entry}\n")


class NetworkEndpoint(ILogDestination):
    def __init__(self, address: str, port: int):
        self.address = address
        self.port = port

    def send_log(self, log_entry: str) -> None:
        print(f"[NETWORK] Sent to {self.address}:{self.port}: {log_entry}")


class SystemJournal(ILogDestination):
    def __init__(self, component: str = "app"):
        self.component = component

    def send_log(self, log_entry: str) -> None:
        print(f"JOURNAL[{self.component.upper()}]: {log_entry}")


class LogProcessor:
    def __init__(
        self,
        conditions: List[ILogCondition],
        outputs: List[ILogDestination],
        add_timestamp: bool = True
    ):
        self.conditions = conditions
        self.outputs = outputs
        self.add_timestamp = add_timestamp

    def process_entry(self, log_entry: str) -> None:
        if not all(cond.is_satisfied(log_entry) for cond in self.conditions):
            return

        formatted_entry = self._format_entry(log_entry)
        for output in self.outputs:
            output.send_log(formatted_entry)

    def _format_entry(self, entry: str) -> str:
        if self.add_timestamp:
            return f"{datetime.now().isoformat()} | {entry}"
        return entry


def demonstrate_logging_system():
    # Создаем условия фильтрации
    critical_condition = TextMatchCondition("CRITICAL")
    warning_condition = TextMatchCondition("WARNING")
    network_condition = RegexCondition(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")

    # Создаем выходные устройства
    terminal = TerminalOutput()
    log_file = FileStorage("application_logs.txt")
    network_log = NetworkEndpoint("logserver.example.com", 514)
    system_log = SystemJournal("webapp")

    # Настраиваем процессоры логов
    critical_processor = LogProcessor(
        [critical_condition],
        [terminal, log_file, system_log]
    )

    warning_processor = LogProcessor(
        [warning_condition],
        [terminal, log_file]
    )

    network_processor = LogProcessor(
        [network_condition],
        [network_log]
    )

    # Тестируем систему
    print("=== Critical Events ===")
    critical_processor.process_entry("CRITICAL: Failed to connect to database")
    critical_processor.process_entry("WARNING: High memory usage")

    print("\n=== Network Events ===")
    network_processor.process_entry("Connection from 192.168.1.1")
    network_processor.process_entry("User logged in")

    print("\n=== Warning Events ===")
    warning_processor.process_entry("WARNING: Disk space low")
    warning_processor.process_entry("INFO: System started")


if __name__ == "__main__":
    demonstrate_logging_system()