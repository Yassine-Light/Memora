"""MemoryAnchor backend entry point."""

import logging

from src.config import settings


def main() -> None:
    logging.basicConfig(level=settings.log_level)
    logging.getLogger(__name__).info(
        "%s started in %s mode using %s",
        settings.app_name,
        settings.environment,
        settings.database_path,
    )


if __name__ == "__main__":
    main()

