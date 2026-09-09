from __future__ import annotations

"""Compatibility entrypoint for the sovereign Healer scheduler.

Historical versions of this module called the GitHub workflow-dispatch API with
HEALER_GH_TOKEN. That production transport is retired. Scheduling/execution is
now carried by the single StegVerse resident heartbeat against already
materialized repositories, with TV/TVC as credential/admission authority.

Reusable-task schedules are evaluated inside that same scheduler path through
`reusable_task_scheduler`; no second scheduler, polling loop, or credential route
is introduced.
"""

from reusable_task_scheduler import main


if __name__ == "__main__":
    raise SystemExit(main())
