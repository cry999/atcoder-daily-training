from sortedcontainers import SortedList

N, Q = map(int, input().split())
C = [0] * (N + 1)

last_operate_r = [-1] * (N + 1)
last_operate_c = [-1] * (N + 1)

timeline_r = SortedList()
timeline_c = SortedList()

ans = 0
for i in range(Q):
    q, x = map(int, input().split())

    if q == 1:
        if last_operate_r[x] != -1:
            timeline_r.remove(-last_operate_r[x])

            j = timeline_c.bisect_left(-last_operate_r[x])
            ans += j
        else:
            ans += N
        last_operate_r[x] = i
        timeline_r.add(-last_operate_r[x])
    else:
        if last_operate_c[x] != -1:
            timeline_c.remove(-last_operate_c[x])

            j = timeline_r.bisect_left(-last_operate_c[x])
            ans -= j
        else:
            ans -= len(timeline_r)

        last_operate_c[x] = i
        timeline_c.add(-last_operate_c[x])

    print(ans)
