// 4 窓の紙の重ね順を全列挙し、可視な紙だけを動かす遷移グラフを作る。
// 各表示への逆向き BFS で最短距離を計算し、同じ手数なら次の注文に
// 対応しやすい到達状態を選ぶ。最後に到達する状態だけを JSON に出力する。
// 使用例: build_policy 8 4 patterns.txt > policy.json
#include <algorithm>
#include <array>
#include <fstream>
#include <iostream>
#include <numeric>
#include <queue>
#include <vector>
using namespace std;
int main(int argc, char **argv) {
  if (argc != 4) {
    cerr << "Usage: build_policy <papers> <bits> <patterns.txt>\n";
    return 1;
  }
  int m = atoi(argv[1]), b = atoi(argv[2]);
  if (m < 2 || m > 9 || b < 1 || b > 6) {
    cerr << "unsupported size\n";
    return 1;
  }
  int v = 1 << b;
  double ignored;
  ifstream f(argv[3]);
  if (!f) {
    cerr << "cannot open patterns\n";
    return 1;
  }
  f >> ignored;
  vector<int> pat(m), op(m), black(m);
  for (int &x : pat)
    f >> x;
  vector<string> patterns;
  for (int k = 0; k < m; k++) {
    int x = pat[k];
    string p;
    for (int j = 0; j < b; j++, x /= 3) {
      p += ".01"[x % 3];
      if (x % 3)
        op[k] |= 1 << j;
      if (x % 3 == 2)
        black[k] |= 1 << j;
    }
    patterns.push_back(p);
  }
  vector<array<unsigned char, 9>> ps;
  array<unsigned char, 9> a{};
  iota(a.begin(), a.begin() + m, 0);
  do {
    ps.push_back(a);
  } while (next_permutation(a.begin(), a.begin() + m));
  int n = ps.size();
  vector<int> fact(m + 1, 1);
  for (int i = 1; i <= m; i++)
    fact[i] = fact[i - 1] * i;
  auto rank = [&](const array<unsigned char, 9> &p) {
    int r = 0, used = 0;
    for (int i = 0; i < m; i++) {
      r += (p[i] - __builtin_popcount((unsigned)used & ((1 << p[i]) - 1))) *
           fact[m - i - 1];
      used |= 1 << p[i];
    }
    return r;
  };
  vector<vector<pair<int, int>>> adj(n);
  vector<vector<int>> rev(n);
  vector<int> display(n);
  for (int s = 0; s < n; s++) {
    int cov = 0, z = 0;
    for (int i = 0; i < m; i++) {
      int k = ps[s][i], ex = op[k] & ~cov;
      z |= black[k] & ex;
      cov |= op[k];
      if (!ex)
        continue;
      for (int d = 0; d < m; d++)
        if (d != i) {
          a = ps[s];
          if (i < d)
            rotate(a.begin() + i, a.begin() + i + 1, a.begin() + d + 1);
          else
            rotate(a.begin() + d, a.begin() + i, a.begin() + i + 1);
          int t = rank(a);
          adj[s].push_back({t, k * m + d});
          rev[t].push_back(s);
        }
    }
    display[s] = z;
  }
  vector<vector<int>> ds(v, vector<int>(n, 1000)), ord(v),
      nxt(v, vector<int>(n)), move(v, vector<int>(n));
  vector<vector<double>> opt(v, vector<double>(n));
  for (int t = 0; t < v; t++) {
    auto &q = ord[t];
    for (int s = 0; s < n; s++)
      if (display[s] == t)
        ds[t][s] = 0, q.push_back(s);
    for (int l = 0; l < (int)q.size(); l++) {
      int s = q[l];
      for (int u : rev[s])
        if (ds[t][u] > ds[t][s] + 1)
          ds[t][u] = ds[t][s] + 1, q.push_back(u);
    }
    if ((int)q.size() != n) {
      cerr << "unreachable";
      return 1;
    }
  }
  vector<double> h(n), nh(n);
  double g = 0;
  for (int it = 0; it < 40; it++) {
    for (int t = 0; t < v; t++)
      for (int s : ord[t]) {
        nxt[t][s] = s;
        move[t][s] = -1;
        if (!ds[t][s]) {
          opt[t][s] = h[s];
          continue;
        }
        opt[t][s] = 1e9;
        for (auto [u, mv] : adj[s])
          if (ds[t][u] + 1 == ds[t][s] && opt[t][u] < opt[t][s] - 1e-10)
            opt[t][s] = opt[t][u], nxt[t][s] = u, move[t][s] = mv;
      }
    for (int s = 0; s < n; s++) {
      nh[s] = 0;
      for (int t = 0; t < v; t++)
        nh[s] += ds[t][s] + opt[t][s];
      nh[s] /= v;
    }
    g = nh[0];
    for (int s = 0; s < n; s++)
      h[s] = nh[s] - g;
  }
  vector<int> ids(n, -1), states{0};
  ids[0] = 0;
  vector<vector<pair<int, vector<int>>>> policy;
  for (int i = 0; i < (int)states.size(); i++) {
    int s = states[i];
    vector<pair<int, vector<int>>> row;
    for (int t = 0; t < v; t++) {
      int u = s;
      vector<int> moves;
      while (ds[t][u]) {
        moves.push_back(move[t][u]);
        u = nxt[t][u];
      }
      if (ids[u] < 0)
        ids[u] = states.size(), states.push_back(u);
      row.push_back({ids[u], moves});
    }
    policy.push_back(row);
  }
  vector<double> p(states.size()), np(states.size());
  p[0] = 1;
  for (int it = 0; it < 200; it++) {
    fill(np.begin(), np.end(), 0);
    for (int s = 0; s < (int)states.size(); s++)
      for (int t = 0; t < v; t++)
        np[policy[s][t].first] += p[s] / v;
    p.swap(np);
  }
  vector<double> grad(v);
  double exact = 0;
  for (int s = 0; s < (int)states.size(); s++)
    for (int t = 0; t < v; t++) {
      auto [u, moves] = policy[s][t];
      exact += p[s] * moves.size() / v;
      grad[t] += p[s] * (moves.size() + h[states[u]]);
    }
  cerr << "states=" << states.size() << " avg=" << exact << " value=" << g
       << endl;
  cout << "{\"patterns\":[";
  for (int k = 0; k < m; k++)
    cout << (k ? "," : "") << '"' << patterns[k] << '"';
  cout << "],\"gradient\":[";
  for (int t = 0; t < v; t++)
    cout << (t ? "," : "") << grad[t];
  cout << "],\"orders\":[";
  for (int i = 0; i < (int)states.size(); i++) {
    if (i)
      cout << ',';
    cout << '[';
    for (int j = 0; j < m; j++)
      cout << (j ? "," : "") << (int)ps[states[i]][j];
    cout << ']';
  }
  cout << "],\"policy\":[";
  for (int s = 0; s < (int)policy.size(); s++) {
    if (s)
      cout << ',';
    cout << '[';
    for (int t = 0; t < v; t++) {
      if (t)
        cout << ',';
      auto [u, mvs] = policy[s][t];
      cout << '[' << u << ",[";
      for (int i = 0; i < (int)mvs.size(); i++)
        cout << (i ? "," : "") << mvs[i];
      cout << "]]";
    }
    cout << ']';
  }
  cout << "]}\n";
}
