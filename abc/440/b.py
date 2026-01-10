N = int(input())
(*T,) = map(int, input().split())
print(*map(lambda x: x[1] + 1, sorted([(t, i) for i, t in enumerate(T)])[:3]))
