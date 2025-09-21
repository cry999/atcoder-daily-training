def s_to_bit(s: str) -> int:
    n = 0
    for c in s:
        if c == '#':
            n |= 1
        n <<= 1
    return n >> 1


def bit_to_s(n: int, digit: int) -> str:
    s = ['.'] * digit
    while digit:
        if n & 1:
            s[digit-1] = '#'
        digit -= 1
        n >>= 1
    return ''.join(s)


def diff(dst: int, src: int) -> int:
    d = 0
    while dst or src:
        if dst % 2 and not (src % 2):  # 白から黒には変えない
            return float('inf')
        if dst % 2 != src % 2:
            d += 1
        dst, src = dst >> 1, src >> 1
    return d


def found_black4(line: int, next_line: int) -> bool:
    while line and next_line:
        if line & 0b11 == next_line & 0b11 == 0b11:
            return True
        line, next_line = line >> 1, next_line >> 1
    return False


T = int(input())

for _ in range(T):
    H, W = map(int, input().split())
    S = [input() for _ in range(H)]

    dp = [[float('inf')]*(1 << W) for _ in range(H)]
    for j in range(1 << W):
        dp[0][j] = diff(j, s_to_bit(S[0]))
    for i in range(H-1):
        for j in range(1 << W):
            if diff(j, s_to_bit(S[i+1])) == float('inf'):
                dp[i+1][j] = float('inf')
            else:
                for k in range(1 << W):
                    if found_black4(j, k):
                        continue
                    dp[i+1][j] = min(
                        dp[i+1][j],
                        dp[i][k] + diff(j, s_to_bit(S[i+1])),
                    )
    print(min(a for a in dp[H-1]))
