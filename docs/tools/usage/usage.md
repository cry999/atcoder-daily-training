# `atcoder usage` 利用手引

`atcoder` の各サブコマンドの**利用頻度・所要時間**をローカルに記録し、`atcoder usage` で集計して見るためのコマンド。「どのコマンド/フラグが実際によく使われ、どれが使われていないか」を定量データで把握し、コマンド設計 (フラグの要否・廃止候補・既定値の見直し) に役立てるのが目的。

> 要件詳細: [requirements/037-usage-telemetry.md](../requirements/037-usage-telemetry.md)

## 仕組み

- `atcoder` を実行するたびに、`main()` が dispatch をラップして 1 イベントをローカルに追記する (JSONL)。
- 記録するのは **サブコマンド名・使われたフラグ名・所要時間・exit code・時刻・バージョン** のみ。**フラグの値や位置引数 (パス・問題名など) は記録しない**。
- ネットワークには一切出さない。完全にローカル完結。
- 記録は **best-effort** — 書き込みに失敗してもコマンド本体の出力・exit code には一切影響しない。
- 補完ヘルパ (`__complete`) と未知コマンド (typo) は記録対象外。

## コマンド

```sh
atcoder usage            # コマンド別の集計表 (count 降順)
atcoder usage --flags    # 上記 + コマンド配下にフラグ別の利用回数
atcoder usage --json     # 集計結果を JSON で出力 (機械可読)
```

### 出力例

```
$ atcoder usage
Command   Count   Total     Avg     Last
test        142   18m02s    7.6s    2026-06-12 14:01
start        37   2h11m     3.5m    2026-06-11 22:40
new          21    4.2s     0.2s    2026-06-12 09:00
stats         9    1.1s     0.1s    2026-06-10 23:12

合計 209 回 / 4 コマンド
```

- **Count**: 実行回数
- **Total**: 合計所要時間
- **Avg**: 1 回あたりの平均所要時間
- **Last**: 最終利用日時 (ローカルタイム)

```
$ atcoder usage --flags
test        142   18m02s    7.6s    2026-06-12 14:01
    task     130
    refresh   12
    submit     4
...
```

## 保存先

```
$XDG_DATA_HOME/atcoder-tools/usage/events.jsonl
```

`XDG_DATA_HOME` が未設定なら `~/.local/share/atcoder-tools/usage/events.jsonl`。**キャッシュ (`$XDG_CACHE_HOME/atcoder-tools/`) とは別のデータ領域**に置くので、`--refresh` 等のキャッシュ操作では消えない (集計の材料として蓄積する)。

1 行 = 1 実行のイベント:

```json
{"ts":"2026-06-12T14:01:09+09:00","cmd":"test","flags":["task"],"dur_ms":7600,"exit":0,"version":"a1b2c3d (..)"}
```

## 記録を無効化する

環境変数 `ATCODER_NO_USAGE` を非空にすると、記録を完全にスキップする (ログファイルも作らない)。

```sh
export ATCODER_NO_USAGE=1   # 以降、利用イベントを記録しない
```

無効化中でも、既に蓄積済みのログがあれば `atcoder usage` で集計は見られる。

## プライバシー

- 記録はフラグ**名**のみ。`--task d e.py` は `cmd=test flags=["task"]` となり、値 `d` や位置引数 `e.py` は残らない。
- ローカルのみ。外部送信は一切ない。
- 不要なら `ATCODER_NO_USAGE` で止められ、`events.jsonl` を消せば履歴も消える。

## exit code

| 状況 | code |
|---|---|
| 集計表示 / 記録なし (メッセージ表示) | 0 |
| ログ読み取りの I/O エラー | 1 |
| 未知フラグ | 2 |

## 関連

- [requirements/037-usage-telemetry.md](../requirements/037-usage-telemetry.md) — 要件定義
- [docs/tools/usage/stats.md](stats.md) — 練習解答の集計 (`stats`。本コマンドとは責務が別)
