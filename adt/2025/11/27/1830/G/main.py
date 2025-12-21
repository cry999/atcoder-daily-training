S = input()
K = int(input())

# SS[i]: S の先頭 i 文字までに含まれる '.' の数
SS = [0] * (len(S)+1)

for i in range(len(S)):
    SS[i+1] = SS[i]+(S[i] == '.')


def check(n: int) -> bool:
    for i in range(len(S)):
        j = i+n
        if j > len(S):
            break
        if SS[j]-SS[i] <= K:
            return True
    return False


lo, hi = 0, len(S)+1
while hi - lo > 1:
    mi = (lo + hi) // 2
    if check(mi):
        lo = mi
    else:
        hi = mi
print(lo)
