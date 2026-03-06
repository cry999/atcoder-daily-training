N = int(input())
(*Q,) = map(int, input().split())
(*A,) = map(int, input().split())
(*B,) = map(int, input().split())

max_a = min(q // a for q, a in zip(Q, A) if a > 0)
max_b = min(q // b for q, b in zip(Q, B) if b > 0)

if max_a > max_b:
    A, B = B, A
    max_a, max_b = max_b, max_a

ans = 0
for x in range(max_a + 1):
    y = min((q - a * x) // b for q, a, b in zip(Q, A, B) if b > 0)
    ans = max(ans, x + y)

print(ans)
