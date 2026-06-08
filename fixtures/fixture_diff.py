# fixture: 出力に複数 token / 複数行があり、一部だけが間違っているケース。
# intra-line token-level diff highlight の見栄えを確認するためのもの。
#   expected: "1 2 3 4 5\nhello world\nlast line"
#   actual:   "1 2 9 4 5\nhello mars\nlast line"
# 行 1 と 2 のそれぞれ 1 token だけが異なる (3→9, world→mars)。
# 行 3 は完全一致なので diff には現れない。
_ = input()
print("1 2 9 4 5")
print("hello mars")
print("last line")
