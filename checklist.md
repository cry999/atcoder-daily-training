# 競プロ困った時のチェックリスト

## 困った時の観点リスト

1. 主役は何か？
    - 値、位置、区間、集合、状態、グラフ？
2. 要素同士の関係は何か？
    - 隣接、大小、親子、依存、到達可能？
3. 個々の値の特徴は何か？
    - parity, mod, bit, 符号, 重複, 値域？
4. 全体の特徴は何か？
    - N, Q, sum, 木, DAG, ソート済み, クエリ多い？
5. 操作で変わるものは何か？
6. 操作で変わらないものは何か？
7. 答えるべき問いは何か？
    - max, min, count, existence?
8. 必要な操作セットは何か？
    - update, query, min, kth, connectivity?
9. それを愚直にやると何が重いか？
10. その重い部分を前処理・累積・データ構造で置き換えられるか？

## 二分探索境界早見表


| 求めたい位置              | 関数                   | 意味                     |
| ------------------- | -------------------- | ---------------------- |
| `x` 以上が初めて現れる位置     | `bisect_left(A, x)`  | `A[i] >= x` となる最小の `i` |
| `x` より大きい値が初めて現れる位置 | `bisect_right(A, x)` | `A[i] > x` となる最小の `i`  |
| `x` を重複の左側に挿入       | `bisect_left(A, x)`  | 同じ値の前                  |
| `x` を重複の右側に挿入       | `bisect_right(A, x)` | 同じ値の後                  |


| 条件を満たす要素 |                 境界位置 |                                       個数 |
| -------- | -------------------: | ---------------------------------------: |
| `a < x`  |  `bisect_left(A, x)` |                      `bisect_left(A, x)` |
| `a <= x` | `bisect_right(A, x)` |                     `bisect_right(A, x)` |
| `a >= x` |  `bisect_left(A, x)` |             `len(A) - bisect_left(A, x)` |
| `a > x`  | `bisect_right(A, x)` |            `len(A) - bisect_right(A, x)` |
| `a == x` |                 左右の差 | `bisect_right(A, x) - bisect_left(A, x)` |


| 値の範囲          | 個数                                        |
| ------------- | ----------------------------------------- |
| `L <= a <= R` | `bisect_right(A, R) - bisect_left(A, L)`  |
| `L <= a < R`  | `bisect_left(A, R) - bisect_left(A, L)`   |
| `L < a <= R`  | `bisect_right(A, R) - bisect_right(A, L)` |
| `L < a < R`   | `bisect_left(A, R) - bisect_right(A, L)`  |


| 求めたい値        | 添字                       |
| ------------ | ------------------------ |
| `x` 以上の最小値   | `bisect_left(A, x)`      |
| `x` より大きい最小値 | `bisect_right(A, x)`     |
| `x` 以下の最大値   | `bisect_right(A, x) - 1` |
| `x` 未満の最大値   | `bisect_left(A, x) - 1`  |


```python
# x 未満の個数
bisect_left(A, x)

# x 以下の個数
bisect_right(A, x)

# x 以上の最小値
A[bisect_left(A, x)]

# x 以下の最大値
A[bisect_right(A, x) - 1]
```
