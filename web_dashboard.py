import logging

log = logging.getLogger(__name__)

class WebDashboard:
    """Placeholder for a web-based control panel."""
    def __init__(self, trainer) -> None:
        self.trainer = trainer
        self.running = False

    def start(self) -> None:
        self.running = True
        log.info("Web dashboard started")

    def stop(self) -> None:
        self.running = False
        log.info("Web dashboard stopped")
