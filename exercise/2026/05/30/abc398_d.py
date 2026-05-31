N, R, C = map(int, input().split())
S = input()

takigi_r, takigi_c = 0, 0
r, c = R, C
takigi_traces = set()
takigi_traces.add((takigi_r, takigi_c))

ans = []
for s in S:
    if s == "N":
        takigi_r += 1
        r += 1
    elif s == "S":
        takigi_r -= 1
        r -= 1
    elif s == "E":
        takigi_c -= 1
        c -= 1
    elif s == "W":
        takigi_c += 1
        c += 1
    takigi_traces.add((takigi_r, takigi_c))
    if (r, c) in takigi_traces:
        ans.append("1")
    else:
        ans.append("0")

print("".join(ans))
