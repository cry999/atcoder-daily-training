S = input()
T = input()

hist_s = {}
hist_t = {}

for i in range(len(S)):
    s, t = S[i], T[i]

    hist_s[s] = hist_s.get(s, 0) + 1
    hist_t[t] = hist_t.get(t, 0) + 1

# s の文字列を処理する
for k, v in hist_s.items():
    if k == '@':
        continue
    if k in hist_t:
        d = min(hist_t[k], v)
        hist_s[k] = v = v-d
        hist_t[k] -= d
    if not v:
        continue
    if k not in 'atcoder':
        continue
    if '@' not in hist_t:
        continue
    # '@' で代用する
    d = min(hist_t['@'], v)
    hist_s[k] = v = v-d
    hist_t['@'] -= d

# t の残りの文字列を処理する
for k, v in hist_t.items():
    if k == '@':
        continue
    if k in hist_s:
        d = min(hist_s[k], v)
        hist_t[k] = v = v-d
        hist_s[k] -= d
    if not v:
        continue
    if k not in 'atcoder':
        continue
    if '@' not in hist_t:
        continue
    d = min(hist_s['@'], v)
    hist_t[k] = v = v-d
    hist_s['@'] -= d

if hist_s.get('@', 0) and hist_t.get('@', 0):
    d = min(hist_s['@'], hist_t['@'])
    hist_s['@'] -= d
    hist_t['@'] -= d

print('No' if any(hist_s.values()) else 'Yes')
# print(f'{hist_s=}')
# print(f'{hist_t=}')
