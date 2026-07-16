N, M = map(int, input().split())
place = [tuple(map(int, input().split())) for _ in range(M)]
can_place_row = [True] * N
can_place_col = [True] * N

place.reverse()

ans = 0
for r, c in place:
    r, c = r - 1, c - 1
    if can_place_row[r] and can_place_col[c]:
        ans += 1
    can_place_row[r] = False
    can_place_col[c] = False
print(ans)
