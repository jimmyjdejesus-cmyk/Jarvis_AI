
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

# Changelog

## 2025-12-14 — Legacy runtime archived (v0.0.0-legacy-archive-2025-12-14)

- Archived the `legacy/` runtime and created a snapshot release `v0.0.0-legacy-archive-2025-12-14` with
  asset `legacy_snapshot_2025-12-14.tar.gz` for retrieval if needed.
- Marked legacy-related endpoints (`/memory/sync/to-legacy`, `/memory/sync/from-legacy`) as **DEPRECATED** in
  the OpenAPI spec and updated documentation to reference the archive and restore steps.
- Updated tests to skip legacy-only checks when the legacy runtime is not present.

Notes:
- To restore the legacy runtime locally, download the release asset and extract it into the repo root as `legacy/`,
  or restore from the archived path in git history. See `README.md` and `docs/MIGRATION_GUIDE.md` for details.
