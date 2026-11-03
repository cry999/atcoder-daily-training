// 不採用の比較実験。両色単窓基底＋疎模様、可視不一致だけを退ける。
#include <algorithm>
#include <array>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <unordered_set>
#include <vector>
using namespace std;
using U = uint64_t;
struct State {
  array<unsigned char, 192> q;
  U display;
  float h;
  int parent, k, d;
};
struct Cand {
  float h;
  U display;
  int parent, k, d;
};
int main(int argc, char **argv) {
  int degree = argc > 1 ? atoi(argv[1]) : 3,
      width = argc > 2 ? atoi(argv[2]) : 4;
  int N, K, P, R;
  if (!(cin >> N >> K >> P >> R))
    return 0;
  vector<string> A(P);
  vector<U> targets(P);
  for (int a = 0; a < P; a++) {
    cin >> A[a];
    for (int j = 0; j < N; j++)
      if (A[a][j] == '1')
        targets[a] |= 1ULL << j;
  }
  vector<U> mask(K), black(K);
  mt19937 rng(74);
  for (int j = 0; j < 64; j++) {
    mask[2 * j] = mask[2 * j + 1] = 1ULL << j;
    black[2 * j + 1] = 1ULL << j;
  }
  vector<int> cols;
  for (int z = 0; z < degree; z++)
    for (int j = 0; j < 64; j++)
      cols.push_back(j);
  shuffle(cols.begin(), cols.end(), rng);
  for (int k = 128; k < K; k++) {
    int pi = rng() % P;
    for (int z = 0; z < degree; z++) {
      int j = cols[(k - 128) * degree + z];
      mask[k] |= 1ULL << j;
    }
    black[k] = targets[pi] & mask[k];
  }
  // 重ね順は初めからランダムな短絡紙を上に置く。
  State cur;
  for (int i = 0; i < 64; i++)
    cur.q[i] = 128 + i;
  for (int i = 0; i < 128; i++)
    cur.q[i + 64] = i;
  cur.display = 0;
  U cov = 0;
  for (int k : cur.q) {
    cur.display |= black[k] & ~cov;
    cov |= mask[k];
  }
  // 出力の紙番号は初期順に合わせて変更する。
  vector<U> nm(K), nb(K);
  for (int i = 0; i < K; i++)
    nm[i] = mask[cur.q[i]], nb[i] = black[cur.q[i]];
  mask = nm;
  black = nb;
  iota(cur.q.begin(), cur.q.end(), 0);
  for (int k = 0; k < K; k++) {
    for (int j = 0; j < N; j++)
      cout << ((mask[k] >> j & 1) ? char('0' + (black[k] >> j & 1)) : '.');
    cout << '\n';
  }
  cout.flush();
  auto apply = [&](State s, int k, int d, U disp) {
    int i = find(s.q.begin(), s.q.end(), k) - s.q.begin();
    if (i < d)
      rotate(s.q.begin() + i, s.q.begin() + i + 1, s.q.begin() + d + 1);
    else
      rotate(s.q.begin() + d, s.q.begin() + i, s.q.begin() + i + 1);
    s.display = disp;
    return s;
  };
  for (int turn = 0; turn < R; turn++) {
    int a;
    if (!(cin >> a) || a < 0)
      return 0;
    U target = targets[a];
    vector<pair<int, int>> answer;
    vector<vector<State>> layers(1, vector<State>{cur});
    auto hashq = [](const State &s) {
      U h = 1469598103934665603ULL;
      for (int k : s.q)
        h = (h ^ k) * 1099511628211ULL;
      return h;
    };
    unordered_set<U> visited;
    visited.insert(hashq(cur));
    bool solved = cur.display == target;
    int solvedidx = 0, depth = 0;
    for (; !solved && depth < 192; depth++) {
      auto &beam = layers.back();
      vector<Cand> candidates;
      for (int si = 0; si < (int)beam.size(); si++) {
        auto &s = beam[si];
        int first[64], second[64], pos[192];
        U once = 0, twice = 0;
        U visible[192] = {};
        for (int i = 0; i < K; i++)
          pos[s.q[i]] = i;
        for (int i = 0; i < K; i++) {
          int k = s.q[i];
          U e = mask[k] & ~once;
          visible[k] = e;
          U e2 = mask[k] & once & ~twice;
          for (U z = e; z; z &= z - 1)
            first[__builtin_ctzll(z)] = k;
          for (U z = e2; z; z &= z - 1)
            second[__builtin_ctzll(z)] = k;
          twice |= e2;
          once |= mask[k];
        }
        int f1[64], f2[64], b1[64], b2[64];
        for (int j = 0; j < 64; j++) {
          int bad = 0, found = 0;
          f1[j] = f2[j] = -1;
          b1[j] = b2[j] = 0;
          for (int k : s.q)
            if (mask[k] >> j & 1) {
              if (((black[k] ^ target) >> j & 1) == 0) {
                if (found == 0) {
                  f1[j] = k;
                  b1[j] = bad;
                  found++;
                } else {
                  f2[j] = k;
                  b2[j] = bad;
                  break;
                }
              } else
                bad++;
            }
          if (f2[j] < 0)
            b2[j] = bad;
        }
        auto cost = [](int x) { return x ? 1.0f + 0.25f * (x - 1) : 0.0f; };
        float base = 0;
        for (int j = 0; j < 64; j++)
          base += cost(b1[j]);
        for (int k = 0; k < K; k++)
          if (visible[k])
            for (int direction = 0; direction < 2; direction++) {
              U wrong = (black[k] ^ target) & mask[k];
              if (direction == 0 &&
                  (wrong || !(mask[k] & (s.display ^ target))))
                continue;
              if (direction == 1 && !(wrong & visible[k]))
                continue;
              int d = direction ? K - 1 : 0;
              if (pos[k] == d)
                continue;
              float h = base;
              U disp = s.display;
              for (U z = mask[k]; z; z &= z - 1) {
                int j = __builtin_ctzll(z);
                int count = b1[j];
                bool correct = ((black[k] ^ target) >> j & 1) == 0;
                if (direction) {
                  if (correct) {
                    if (k == f1[j])
                      count = b2[j];
                  } else if (pos[k] < pos[f1[j]])
                    count--;
                } else {
                  if (correct)
                    count = 0;
                  else if (pos[k] > pos[f1[j]])
                    count++;
                }
                h += cost(count) - cost(b1[j]);
                if (count)
                  disp = (disp & ~(1ULL << j)) | ((~target) & (1ULL << j));
                else
                  disp = (disp & ~(1ULL << j)) | (target & (1ULL << j));
              }
              candidates.push_back({h, disp, si, k, d});
            }
      }
      sort(candidates.begin(), candidates.end(),
           [](const Cand &a, const Cand &b) { return a.h < b.h; });
      vector<State> next;
      for (auto &c : candidates) {
        State s = apply(beam[c.parent], c.k, c.d, c.display);
        if (!visited.insert(hashq(s)).second)
          continue;
        s.parent = c.parent;
        s.k = c.k;
        s.d = c.d;
        s.h = c.h;
        bool duplicate = false;
        for (auto &t : next)
          if (t.q == s.q)
            duplicate = true;
        if (duplicate)
          continue;
        next.push_back(s);
        if (s.display == target) {
          solved = true;
          solvedidx = next.size() - 1;
          break;
        }
        if ((int)next.size() == width)
          break;
      }
      layers.push_back(next);
    }
    if (!solved) {
      cerr << "stuck " << turn << "\n";
      return 1;
    }
    cur = layers.back()[solvedidx];
    for (int d = layers.size() - 1; d > 0; d--) {
      auto &s = layers[d][solvedidx];
      answer.push_back({s.k, s.d});
      solvedidx = s.parent;
    }
    reverse(answer.begin(), answer.end());
    cout << answer.size() << '\n';
    for (auto [k, d] : answer)
      cout << k << ' ' << d << '\n';
    cout.flush();
  }
}
