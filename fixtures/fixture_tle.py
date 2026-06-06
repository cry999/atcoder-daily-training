# fixture: 制限時間を超過する遅延コード (meta.toml で 200ms 制限なので必ず TLE)
import time
n = int(input())
time.sleep(2)
print(n * 2)
