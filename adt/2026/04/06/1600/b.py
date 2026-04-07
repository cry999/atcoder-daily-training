score_takahashi = sum(map(int, input().split()))
score_aoki = sum(map(int, input().split()))
ans = score_takahashi + 1 - score_aoki
print(ans)
