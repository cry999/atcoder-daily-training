N = int(input())
(*A,) = map(int, input().split())

seen = [[] for _ in range(200)]

for i, a in enumerate(A, 1):
    current = []

    current.append((a % 200, [i]))

    for r, arr in enumerate(seen):
        if not arr:
            continue
        current.append(((r + a) % 200, arr + [i]))

    for r, arr in current:
        if seen[r]:
            print("Yes")
            print(len(seen[r]), *seen[r])
            print(len(arr), *arr)
            exit()
            break
        seen[r] = arr

print("No")
