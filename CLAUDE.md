# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

Personal AtCoder competitive programming practice. Almost all solutions are Python; a small Go module under `cmd/` provides scaffolding tooling.

## Languages & tooling

- **Python 3.13+**, managed by Poetry (`pyproject.toml`). Runtime deps: `sortedcontainers`, `ac-library-python`. Dev: `flake8`.
- **Go 1.25** module `github.com/cry999/atcoder-daily-training` for the `atcoder` helper CLI under `cmd/atcoder/`.
- A `.venv/` is checked in locally; the user runs Python from that venv.

## Common commands

- Run a solution against a sample: `python <path>/main.py < <path>/input-00.txt` (compare to `output-00.txt`).
- Create today's exercise directory (`exercise/YYYY/MM/DD/`): `go run ./cmd/atcoder new`.
- Run a solution against downloaded samples: `go run ./cmd/atcoder test <contest> --task <task>` — on first run it fetches the samples and time limit from AtCoder and caches them, then judges (PASS/FAIL/TLE/RE). `test` also has ad-hoc (`--in`/`--out`), interactive (`--interactive`), and submit-prep (`--submit`) modes; see `docs/tools/usage/test.md`. `atcoder gen <contest> --task <task>` generates random input by best-effort parsing of the problem's constraints + input format (also `:gen` inside the interactive chat); see `docs/tools/usage/gen.md`. `atcoder record <contest> --task <task>` は実装時間・正答状況・5 軸スコアを解答ファイル先頭の solve-stat コメントに記録し `atcoder stats` がそれを集計する (目標時間は `config set target.<category>.<letter>` で設定); see `docs/tools/usage/record.md`. The full subcommand set (`new`/`start`/`test`/`gen`/`meta`/`stats`/`record`/`usage`/`review`/`config`/`login`/`logout`/`update`/`version`/`commit`/`completion`) lives in `cmd/atcoder/`. `atcoder login` imports a browser `REVEL_SESSION` cookie (hand-pasted via `--session-cookie`/stdin) to authenticate, verifies it against a login-gated page, and stores it at `$XDG_DATA_HOME/atcoder-tools/session.toml` (0600); `atcoder logout` discards it. Session handling lives in `internal/atcoder`; see `docs/tools/usage/login.md`. `atcoder usage` reports local CLI usage telemetry (per-command frequency/duration recorded as JSONL under `$XDG_DATA_HOME/atcoder-tools/usage/`; disable with `ATCODER_NO_USAGE`; see `docs/tools/usage/usage.md`).
- Lint Python: `flake8 <path>` (configured as a dev dep, no project-specific config).

There is no project-wide test runner — each problem stands alone, validated by running it against its own sample I/O files when present.

## Directory layout & file conventions

Different sub-trees follow different layouts depending on the source of the problem. Recognizing the layout tells you where to put a new solution.

- `abc/<contest>/<letter>.py` — AtCoder Beginner Contest. One file per problem (`a.py`...`g.py`), no test files alongside.
- `arc/<contest>/<letter>.py`, `awc/<contest>/<letter>.py` — Same shape as `abc/`.
- `adt/<YYYY>/<MM>/<DD>/<HHMM>/<LETTER>/` — AtCoder Daily Training contests bucketed by date + start time (e.g. `1600`, `1800`, `2000`). Each problem letter (`E`, `F`, ...) is its **own directory** containing `main.py` plus `input-NN.txt` / `output-NN.txt` sample pairs.
- `exercise/<YYYY>/<MM>/<DD>/<file>.py` — Daily practice. Files are flat under the date dir and named after the source problem (e.g. `abc357_d.py`).
- `dp/<LETTER>/` — Educational DP Contest (A–Z). Same per-problem-directory shape as `adt/.../<LETTER>/`: `main.py` + `input-NN.txt` / `output-NN.txt`. Some dirs also have an `old/` subdir with earlier attempts.
- `tessoku-book/` — Flat files `a09.py`–`a77.py`, `b09.py`–`b69.py`, `c01.py`–`c12.py` (one per book problem).
- `nikkei2019-final/`, `spoj/`, `2025/<MM>/<DD>/<contest>/` — Older / one-off practice trees.
- `roadmaps/` — Topic-organized practice plans (e.g. `2026-graph.md`) listing AtCoder problem URLs as checklists. Use these to understand what the user is working through.

When adding a solution, match the layout already in use for that sub-tree (don't introduce per-problem dirs in `abc/`, and don't flatten `dp/` or `adt/`).

## Solution style

- Solutions are written terse and idiomatic for competitive programming: short variable names, `input()`/`print()` I/O, minimal abstraction. Don't restructure for "clean code" — match the style of nearby files.
- Modulus `998244353` and `10**9+7` patterns are common.
- Japanese comments are used freely to explain reasoning steps; preserve them when editing.

## Tracked status

`.gitignore` only excludes `/target`. Stray files at the repo root (`test.txt`, `output.txt`, `test.output`, `example_01*.txt`) appear to be ad-hoc scratch I/O — don't treat them as canonical inputs.

## Workflow rules

- **Always work in a `git worktree`.** For every new instruction (anything beyond reading or trivial inspection), create a fresh worktree off `main` first, do the work + commit there, then merge back to `main` and remove the worktree.

  ```sh
  # branch name should describe the task, e.g. feat-chat-resize, fix-tle-display, doc-cache-paths
  git worktree add ../atcoder-daily-training.worktrees/<branch> -b <branch>
  cd ../atcoder-daily-training.worktrees/<branch>
  # ...work...
  git commit -m "..."
  cd -
  git merge --ff-only <branch>      # (or non-ff if separate branch history is meaningful)
  git worktree remove ../atcoder-daily-training.worktrees/<branch>
  git branch -d <branch>
  ```

  Worktree path convention: sibling to the main checkout under `../atcoder-daily-training.worktrees/<branch>/`. One worktree per coherent task; don't reuse worktrees across unrelated changes.

- **Manage TODOs in `docs/tools/todo.md`.** Ongoing tasks and improvement ideas for the `atcoder` tool are tracked there (ABC 本番対応のロードマップは `docs/tools/abc-todo.md`). When adding, picking up, or completing a TODO, update that file rather than tracking it elsewhere.
