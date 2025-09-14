N = int(input())
L = list(map(int, input().split()))

try:
    left, right = L.index(1) + 1, len(L) - list(reversed(L)).index(1)
    print(right - left)
except ValueError:
    print(0)
