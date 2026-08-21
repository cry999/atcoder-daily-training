from sortedcontainers import SortedList

N = int(input())
A = SortedList(list(map(int, input().split())))
A.add(0)

cur_i = A.bisect_left(0)
ans = 0
while A:
    cur_v = A.pop(cur_i)
    if not A:
        break

    if cur_i == 0:
        nxt_v = A[cur_i]
        nxt_i = cur_i
    elif cur_i == len(A):
        nxt_v = A[cur_i - 1]
        nxt_i = cur_i - 1
    else:
        if cur_v - A[cur_i - 1] <= A[cur_i] - cur_v:
            nxt_v = A[cur_i - 1]
            nxt_i = cur_i - 1
        else:
            nxt_v = A[cur_i]
            nxt_i = cur_i

    ans += abs(cur_v - nxt_v)
    cur_i = nxt_i

print(ans)
