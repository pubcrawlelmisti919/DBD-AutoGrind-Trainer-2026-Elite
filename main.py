import asyncio
import logging
from rich.logging import RichHandler
from gui import launch_gui

logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("DBD-Trainer")

def main() -> None:
    """Entry point: launch the trainer GUI."""
    log.info("Starting DBD AutoGrind Trainer 2026")
    launch_gui()

if __name__ == "__main__":
    main()
