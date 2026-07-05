# 桁 DP 練習

|  順 | 問題                                    | 何を練習できるか                                                                                      |
| -: | ------------------------------------- | --------------------------------------------------------------------------------------------- |
|  1 | **EDPC S - Digit Sum**                | 桁 DP の基本形。`less` と `mod` だけ。桁和が `D` の倍数の数を数える問題です。`K < 10^10000` なので桁 DP の典型です。([AtCoder][1]) |
|  2 | **ABC154 E - Almost Everywhere Zero** | leading zero と「0 でない数字の個数」を管理する練習。`N < 10^100`, `K <= 3` なので状態が小さいです。([AtCoder][2])           |
|  3 | **ABC007 D - 禁止された数字**                | 区間 `[A, B]` を `f(B) - f(A-1)` にする練習。数字 `4` と `9` を含む数を数えます。([AtCoder][3])                     |
|  4 | **ABC029 D - 1**                      | 「個数」だけでなく「数字 1 が何回出たか」の総和を数える練習。`1` の出現回数を合計する問題です。([AtCoder][4])                             |
|  5 | **ABC465 E - Count by 3 Conditions**  | 今回の問題。`使った数字集合 bitmask`、`mod 3`、`less` を持つ練習にちょうどよいです。                                        |
|  6 | **ABC208 E - Digit Products**         | 各桁の積を管理する応用。`N <= 10^18`, `K <= 10^9` で、単純な積状態をどう圧縮するかがポイントです。([AtCoder][5])                  |
|  7 | **ABC235 F - Variety of Digits**      | `使った数字集合` に加えて「数の総和」も管理する問題。ABC465 E の次にかなり相性がよいです。([AtCoder][6])                             |
|  8 | **ABC336 E - Digit Sum Divisible**    | 桁和を固定して、`n % digit_sum == 0` を判定する発展問題。`N <= 10^14` ですが状態設計が一段難しいです。([AtCoder][7])            |

[1]: https://atcoder.jp/contests/dp/tasks/dp_s "S - Digit Sum"
[2]: https://atcoder.jp/contests/abc154/tasks/abc154_e "E - Almost Everywhere Zero"
[3]: https://atcoder.jp/contests/abc007/tasks/abc007_4 "D - 禁止された数字"
[4]: https://atcoder.jp/contests/abc029/tasks/abc029_d "D - 1"
[5]: https://atcoder.jp/contests/abc208/tasks/abc208_e "E - Digit Products"
[6]: https://atcoder.jp/contests/abc235/tasks/abc235_f "F - Variety of Digits"
[7]: https://atcoder.jp/contests/abc336/tasks/abc336_e "E - Digit Sum Divisible"

チェック

- [x] 1
- [ ] 2
- [ ] 3
- [ ] 4
- [ ] 5
- [ ] 6
- [ ] 7
- [ ] 8
