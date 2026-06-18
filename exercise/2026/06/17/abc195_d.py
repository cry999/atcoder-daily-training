N, M, Q = map(int, input().split())

luggage = []
for _ in range(N):
    w, v = map(int, input().split())
    luggage.append((v, w))
luggage.sort(reverse=True)

(*boxes,) = map(int, input().split())

for _ in range(Q):
    l, r = map(int, input().split())

    usable_boxes = []
    for i in range(l - 1):
        usable_boxes.append(boxes[i])
    for i in range(r, M):
        usable_boxes.append(boxes[i])

    usable_boxes.sort()
    used = [False] * len(usable_boxes)

    ans = 0
    for i in range(N):
        v, w = luggage[i]
        for j, box in enumerate(usable_boxes):
            if not used[j] and w <= box:
                used[j] = True
                ans += v
                break
    print(ans)
