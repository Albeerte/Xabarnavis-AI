#!/usr/bin/env python
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    project_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_dir))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xabarnavis_admin.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
