# Test fixtures

`exercise test` コマンドの挙動を手動で確認するためのフィクスチャ群。
当日の演習ディレクトリ (`exercise/YYYY/MM/DD/`) を汚さずに済むよう、`--exercise-dir fixtures` で明示的に参照する。

## 実行例

```sh
# ビルドしておく
go build -o /tmp/exercise-bin ./cmd/exercise

# 全 PASS
/tmp/exercise-bin test fixture --task pass  --exercise-dir fixtures

# FAIL (off-by-one)
/tmp/exercise-bin test fixture --task fail  --exercise-dir fixtures

# RE (Runtime Error)
/tmp/exercise-bin test fixture --task re    --exercise-dir fixtures

# TLE (sleep が time_limit=200ms を超過)
/tmp/exercise-bin test fixture --task tle   --exercise-dir fixtures

# debug: [DEBUG] 行のフィルタを確認
/tmp/exercise-bin test fixture --task debug --exercise-dir fixtures      # FAIL (汚染)
/tmp/exercise-bin test fixture --task debug --exercise-dir fixtures -d   # PASS (フィルタ)
```

| fixture | 入力 | 期待出力 | 挙動 |
|---|---|---|---|
| `fixture_pass` | `5` | `10` | 正答 (N\*2 を出力)。常に PASS |
| `fixture_fail` | `5` | `10` | 誤答 (N\*2+1)。常に FAIL |
| `fixture_re` | `5` | `10` | `RuntimeError` を raise。常に RE |
| `fixture_tle` | `5` | `10` | `time.sleep(2)` 後に出力。`time_limit=200ms` で常に TLE |
| `fixture_debug` | `5` | `10` | `[DEBUG]` 行を常時出力。`-d` 無し → FAIL、`-d` 付き → PASS |

## ディレクトリ構造

各 fixture は要件定義の規約 (`<task>.py` + 同名ディレクトリ配下に `meta.toml` と `tests/NN.in NN.out`) を踏襲している。

```
fixtures/
  fixture_pass.py
  fixture_pass/
    meta.toml
    tests/
      01.in
      01.out
  fixture_fail.py
  fixture_fail/
    ...
```
