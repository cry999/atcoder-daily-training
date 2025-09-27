import bisect


N, M = map(int, input().split())
A = list(sorted(map(int, input().split())))
B = list(sorted(map(int, input().split())))

C = sorted(A + B)

prev_a = False
for c in C:
    i = bisect.bisect_left(A, c)
    if i < N and A[i] == c:
        if prev_a:
            print('Yes')
            break
        prev_a = True
    else:
        prev_a = False
else:
    print('No')


# count_a = 0
# ai, bi = 0, 0
#
# while ai < N and bi < M:
#     if A[ai] < B[bi]:
#         count_a += 1
#         ai += 1
#     else:
#         count_a = 0
#         bi += 1
#     if count_a == 2:
#         print('Yes')
#         break
# else:
#     print('No')
