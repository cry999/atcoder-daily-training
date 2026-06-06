---
name: test-tool
description: Run the fixture-based smoke test for the `exercise test` CLI by invoking ./fixtures/run.sh. Use after refactoring or extending cmd/exercise, internal/runner, internal/testexec, or internal/ui — it asserts expected exit codes across PASS/FAIL/RE/TLE and the DEBUG-filter paths. Do NOT use for changes confined to docs, practice solutions (exercise/, abc/, adt/, dp/, …), or unrelated tooling.
---

# test-tool

Smoke-test the `exercise test` CLI by running every fixture under `fixtures/` and asserting its expected exit code.

## How to invoke

```sh
./fixtures/run.sh
```

The script:

1. Builds the tool with `go build` (output to a temp directory).
2. Stages `fixtures/fixture_*` (both the `.py` files and their sibling `<task>/{meta.toml,tests/}` dirs) into a freshly-created temp `exercise/YYYY/MM/DD/` tree.
3. `cd`s into that temp staging dir and invokes the tool with `test fixture --task <name>` (plus `-d` for the debug-filter case).
4. Asserts the expected exit code for each fixture (see `fixtures/README.md`).
5. Prints `All fixtures behaved as expected.` on success, or `N case(s) failed` and exits non-zero on regression.

## When to invoke

Use this skill after edits to any of:

- `cmd/exercise/` — argument parsing, dispatch, runner factory.
- `internal/runner/` — process execution.
- `internal/testexec/` — orchestration, judge, meta cache, AtCoder fetch.
- `internal/ui/` — reporter implementation, styles.

Use it also when the user asks to verify the tool / check for regressions.

## When NOT to invoke

Skip this skill when only the following changed:

- Documentation under `docs/` or top-level README/markdown.
- Practice solutions under `exercise/`, `abc/`, `arc/`, `awc/`, `adt/`, `dp/`, `tessoku-book/`, `spoj/`, etc.
- This skill, the fixtures themselves, or unrelated repository housekeeping.

## When it fails

The tool's own output for each fixture is printed before the assertion line. Scroll up to find the offending case and investigate. Re-run after fixing.

For adding a new fixture (when a new behavior is introduced), see `docs/tools/exercise-test-testing.md`.
