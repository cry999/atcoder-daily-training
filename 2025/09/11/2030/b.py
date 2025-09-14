S = input()
idx = S[::-1].index('.')
print(S[len(S)-idx:])
