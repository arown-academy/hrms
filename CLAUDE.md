# hrms (Arown fork of Frappe HR)

GitHub: `arown-academy/hrms` (git remote `upstream`).

## Git branch rules

- Use **only the `version-16` branch**. Commit on `version-16` and push `version-16`.
- **Do not create new branches.**
- **Never use the `develop` branch**: don't base work on it and don't merge from or into it.
  - `develop` is Frappe's next-major-version line, not ours.
  - It was deleted from GitHub on 10 Nov 2026.
- There is no `main` branch. "main" means `version-16`.
- The local clone is shallow, so `git branch --merged` and `git log A..B` give wrong answers. To check whether a branch is merged, use the GitHub compare API: `https://api.github.com/repos/arown-academy/hrms/compare/version-16...<branch>`. `gh` is not installed.

## After changing the PWA frontend (`frontend/`)

- Run `cd frontend && yarn build`, then `bench restart`.
- The build output (`hrms/public/frontend`) is git-ignored, so every server must build after pulling.
