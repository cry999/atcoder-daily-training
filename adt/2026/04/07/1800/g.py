N = int(input())
S = list(input())
Q = int(input())

# i 文字目が最後に変更されたのは何回目のクエリかを記録する
last_query = [-1] * N
# last_2_or_3: 最後に行われた 2 or 3 のクエリはどちらかを記録
# last_2_or_3_query: 最後に行われた 2 or 3 のクエリは何回目のクエリかを記録
last_2_or_3 = 0
last_2_or_3_query = -1

for q in range(Q):
    rt, rx, c = input().split()
    t, x = int(rt), int(rx) - 1

    if t == 1:
        S[x] = c
        last_query[x] = q
    else:
        last_2_or_3 = t
        last_2_or_3_query = q

for i in range(N):
    if last_query[i] >= last_2_or_3_query:
        # 最後の 2 / 3 以降に 1 の操作があった場合はそれが最優先
        S[i] = S[i]
    else:
        # 最後の 2 / 3 以降に操作されていない場合は、最後の 2 / 3 によって
        # 大文字小文字が変更されるので、それを反映させる。
        S[i] = S[i].lower() if last_2_or_3 == 2 else S[i].upper()

print("".join(S))
