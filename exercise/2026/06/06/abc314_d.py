import sys

input = sys.stdin.readline

N = int(input())
S = list(input())

last_swap = [-1] * N  # 各文字が最後に入れ替え操作を行ったのはいつか
last_lower = -1  # 最後に全体小文字操作をしたのはいつか
last_upper = -1  # 最後に全体大文字操作をしたのはいつか

Q = int(input())

for i in range(Q):
    t, raw_x, c = input().split()

    x = int(raw_x) - 1
    if t == "1":
        # swap
        last_swap[x] = i
        S[x] = c
    elif t == "2":
        # lower
        last_lower = i
    else:  # t == '3'
        # upper
        last_upper = i


for i in range(N):
    m = max(last_swap[i], last_lower, last_upper)
    if m == last_swap[i]:
        # そのまま
        pass
    elif m == last_lower:
        S[i] = S[i].lower()
    else:  # m == last_upper
        S[i] = S[i].upper()

print("".join(S))
