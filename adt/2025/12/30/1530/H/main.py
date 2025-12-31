from sortedcontainers import SortedList


N, M, K = map(int, input().split())
(*A,) = map(int, input().split())

# am: a_i から a_{i+M-1} までの M 個を保持
am = SortedList()

for i in range(M):
    am.add(A[i])

ans = [sum(am[k] for k in range(K))]

for i in range(N - M):
    # print(f"remove A[{i}]={A[i]} and add A[{i+M}]={A[i+M]}")
    nxt = ans[-1]
    # まずは A[i] の削除が影響あるかを確認
    j = am.bisect_right(A[i])
    am.remove(A[i])
    if j <= K:
        # ak に変更が起きる
        nxt += (am[K - 1] if am else 0) - A[i]
    else:
        # ak に変更は起きない
        pass

    # 次に A[i+M] の追加が影響あるかを確認
    k = am.bisect_right(A[i + M])
    if k < K:
        nxt += A[i + M] - (am[K - 1] if am else 0)
    else:
        # A[i+M] は ak に影響しない
        pass
    am.add(A[i + M])

    ans.append(nxt)

print(*ans)
