# >>> atcoder-stat >>>
# started_at  = 2026-07-06T17:46:35+09:00
# solved_at   = 2026-07-06T18:03:31+09:00
# duration_ms = 1016020
# ac          = true
# editorial   = false
# knowledge   = 3
# translation = 3
# complexity  = 3
# impl        = 3
# verify      = 3
# <<< atcoder-stat <<<

N = int(input())
(*A,) = map(int, input().split())
A.sort()
(*B,) = map(int, input().split())
B.sort()
(*C,) = map(int, input().split())
C.sort()

D = [0] * (N + 1)
j = N
for i in range(N - 1, -1, -1):
    while j - 1 >= 0 and B[i] < C[j - 1]:
        j -= 1

    D[i] = D[i + 1] + N - j

j = 0
ans = 0
for i in range(N):
    while j < N and A[i] >= B[j]:
        j += 1

    ans += D[j]
print(ans)

# # 尺取法で解きたいけど、教育のため二分探索で解く
#
# # まずは、B[i] と組み合わせられる C[j] の個数をカウントしておく。
# available_c = [0] * N
# for i in range(N):
#     lo, hi = 0, N
#     while hi > lo:
#         mid = (hi + lo) // 2
#         if C[mid] <= B[i]:
#             lo = mid + 1
#         else:
#             hi = mid
#
#     if lo < N and B[i] == C[lo]:
#         lo += 1
#     if lo >= N:
#         break
#     available_c[i] = N - lo
#
# # A[i] から使える B[j] に対して, availbale_c[j] の和が必要になるので累積和をとっておく。
# for i in range(N - 1, 0, -1):
#     available_c[i - 1] += available_c[i]
#
# ans = 0
# for i in range(N):
#     lo, hi = 0, N
#     while hi > lo:
#         mid = (hi + lo) // 2
#         if B[mid] <= A[i]:
#             lo = mid + 1
#         else:
#             hi = mid
#
#     if lo < N and A[i] == B[lo]:
#         lo += 1
#     if lo >= N:
#         break
#
#     ans += available_c[lo]
# print(ans)
