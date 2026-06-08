S = input()
L = len(S)
N = int(input())

# まずは最小値を設定する。
ans = int(S.replace("?", "0"), base=2)

for i, c in enumerate(S):
    if c != "?":
        continue
    bit = 1 << (L - 1 - i)
    if ans + bit <= N:
        ans += bit

if ans > N:
    print(-1)
else:
    print(ans)
