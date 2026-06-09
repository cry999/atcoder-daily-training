N, x, y = map(int, input().split())
(*A,) = map(int, input().split())

dx = [A[i] for i in range(2, N, 2)]
dy = [A[i] for i in range(1, N, 2)]

sx = {A[0]}
for a in dx:
    sx = {v + a for v in sx} | {v - a for v in sx}

sy = {0}
for a in dy:
    sy = {v + a for v in sy} | {v - a for v in sy}

print("Yes" if x in sx and y in sy else "No")

# # N{X,Y} = X, Y それぞれの要素で i の個数。e.g. NX[1] = (A[2*i] = 1 となる個数)
# NX = [0] * (10 + 1)
# NY = [0] * (10 + 1)
# for i, a in enumerate(A):
#     if i == 0:
#         continue
#     if i % 2:
#         NY[a] += 1
#     else:
#         NX[a] += 1
#
# ZERO = 10**5
#
# dp_x = [[False] * (2 * ZERO + 1) for _ in range(11)]
# dp_x[0][A[0] + ZERO] = True
#
# MIN_X, MAX_X = A[0] + ZERO, A[0] + ZERO
# for i in range(10):
#     nxt_min, nxt_max = MIN_X, MAX_X
#     for n in range(NX[i + 1], -1, -2):
#         for d in range(MIN_X, MAX_X + 1):
#             if dp_x[i][d]:
#                 dp_x[i + 1][d + n * (i + 1)] |= dp_x[i][d]
#                 dp_x[i + 1][d - n * (i + 1)] |= dp_x[i][d]
#                 nxt_min = min(nxt_min, d - n * (i + 1))
#                 nxt_max = max(nxt_max, d + n * (i + 1))
#     MIN_X, MAX_X = nxt_min, nxt_max
#
# dp_y = [[False] * (2 * ZERO + 1) for _ in range(11)]
# dp_y[0][ZERO] = True
#
# MIN_Y, MAX_Y = ZERO, ZERO
# for i in range(10):
#     nxt_min, nxt_max = MIN_Y, MAX_Y
#     for n in range(NY[i + 1], -1, -2):
#         for d in range(MIN_Y, MAX_Y + 1):
#             if dp_y[i][d]:
#                 dp_y[i + 1][d + n * (i + 1)] |= dp_y[i][d]
#                 dp_y[i + 1][d - n * (i + 1)] |= dp_y[i][d]
#                 nxt_min = min(nxt_min, d - n * (i + 1))
#                 nxt_max = max(nxt_max, d + n * (i + 1))
#     MIN_Y, MAX_Y = nxt_min, nxt_max
#
# if dp_x[10][x + ZERO] and dp_y[10][y + ZERO]:
#     print("Yes")
# else:
#     print("No")
