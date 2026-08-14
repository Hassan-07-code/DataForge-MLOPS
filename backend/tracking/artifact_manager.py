from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable

from backend.utils.logger import logger


class ArtifactManager:
    """Collect and validate artifact file paths."""

    @staticmethod
    def collect(paths: Iterable[str | os.PathLike]) -> list[str]:
        """
        Return existing artifact files from the supplied paths.

        - Ignores missing paths.
        - Ignores directories.
        - Removes duplicates.
        - Preserves input order.
        """

        if paths is None:
            return []

        artifacts: list[str] = []
        seen: set[str] = set()

        for path in paths:
            if path is None:
                continue

            try:
                path_obj = Path(path)
            except (TypeError, ValueError):
                logger.warning(f"Invalid artifact path ignored: {path!r}")
                continue

            if not path_obj.exists():
                logger.warning(f"Artifact does not exist: {path_obj}")
                continue

            if not path_obj.is_file():
                logger.warning(f"Artifact path is not a file: {path_obj}")
                continue

            normalized = str(path_obj.resolve())

            if normalized in seen:
                continue

            seen.add(normalized)
            artifacts.append(normalized)

        return artifacts