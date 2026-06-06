# fixture: 常に FAIL する誤答 (off-by-one で期待値より 1 大きい値を出力)
n = int(input())
print(n * 2 + 1)
