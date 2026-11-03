// 不採用の比較実験。専用窓から動かせる白コントローラを使う。
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <numeric>
#include <random>
#include <tuple>
#include <vector>
using namespace std;
using U = uint64_t;
int pc(U x) { return __builtin_popcountll(x); }
int main(int argc, char **argv) {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, k, p, r;
  if (!(cin >> n >> k >> p >> r))
    return 0;
  vector<string> ss(p);
  vector<U> codes(p);
  for (int a = 0; a < p; a++) {
    cin >> ss[a];
    for (int j = 0; j < n; j++)
      if (ss[a][j] == '1')
        codes[a] |= U(1) << j;
  }
  int h = argc > 1 ? atoi(argv[1]) : 32, degree = argc > 2 ? atoi(argv[2]) : 3,
      steps = argc > 3 ? atoi(argv[3]) : 200000;
  double ratio = argc > 4 ? atof(argv[4]) : 1.0;
  bool keep_base = argc > 5 ? atoi(argv[5]) : false;
  U rescue = U(1) << 63, hm = (U(1) << h) - 1, cm = ~(hm | rescue), flip = 0;
  int bn = 63 - h, c = 127;
  for (int j = 0; j < 64; j++) {
    int cnt = 0;
    for (U code : codes)
      cnt += code >> j & 1;
    if (cnt < p / 2)
      flip |= U(1) << j;
  }
  for (U &code : codes)
    code ^= flip;
  bool haszero = false;
  for (U code : codes)
    if (!(code & hm))
      haszero = true;
  if (haszero) {
    mt19937 orient(75);
    bool found = false;
    for (int it = 0; it < 10000; it++) {
      U f = U(orient()) & hm;
      bool good = true;
      for (U code : codes)
        if (!((code ^ f) & hm)) {
          good = false;
          break;
        }
      if (good) {
        for (U &code : codes)
          code ^= f;
        flip ^= f;
        found = true;
        break;
      }
    }
    if (!found) {
      cerr << "orientation failure\n";
      return 1;
    }
  }
  auto fallback = [&]() {
    for (int j = 0; j < 64; j++)
      for (int col = 0; col < 2; col++) {
        string s(64, '.');
        s[j] = '0' + col;
        cout << s << '\n';
      }
    for (int z = 128; z < 192; z++)
      cout << string(64, '.') << '\n';
    cout.flush();
    vector<int> cur(64);
    for (int t = 0; t < r; t++) {
      int a;
      if (!(cin >> a) || a < 0)
        return;
      vector<pair<int, int>> out;
      for (int j = 0; j < 64; j++)
        if (cur[j] != ss[a][j] - '0') {
          out.emplace_back(2 * j + cur[j], 2 * j + 1);
          cur[j] ^= 1;
        }
      cout << out.size() << '\n';
      for (auto [x, d] : out)
        cout << x << ' ' << d << '\n';
      cout.flush();
    }
  };
  vector<tuple<int, int, int>> edges;
  for (int a = 0; a < p; a++)
    for (int b = 0; b < a; b++)
      if (codes[a] & codes[b] & hm)
        edges.emplace_back(pc((codes[a] ^ codes[b]) & cm), a, b);
  sort(edges.begin(), edges.end());
  vector<int> used(p);
  vector<vector<int>> cl;
  for (auto [cost, a, b] : edges)
    if (!used[a] && !used[b]) {
      used[a] = used[b] = 1;
      cl.push_back({a, b});
    }
  for (int a = 0; a < p; a++)
    if (!used[a])
      cl.push_back({a});
  auto baseof = [&](const vector<int> &v) {
    U b = ~U(0);
    for (int a : v)
      b &= codes[a];
    return b;
  };
  auto costof = [&](const vector<int> &v) {
    int sum = 0;
    for (int a : v)
      sum += pc(codes[a] & cm);
    return sum - int(v.size()) * pc(baseof(v) & cm);
  };
  while (int(cl.size()) > c) {
    int bi = -1, bj = -1, bc = 100000;
    for (int i = 0; i < int(cl.size()); i++)
      for (int j = 0; j < i; j++) {
        if (!(baseof(cl[i]) & baseof(cl[j]) & hm))
          continue;
        auto v = cl[i];
        v.insert(v.end(), cl[j].begin(), cl[j].end());
        int delta = costof(v) - costof(cl[i]) - costof(cl[j]);
        if (delta < bc) {
          bc = delta;
          bi = i;
          bj = j;
        }
      }
    if (bi < 0) {
      fallback();
      return 0;
    }
    cl[bj].insert(cl[bj].end(), cl[bi].begin(), cl[bi].end());
    cl.erase(cl.begin() + bi);
  }
  if (int(cl.size()) != c) {
    fallback();
    return 0;
  }
  mt19937 rng(74);
  auto real = [&]() { return (rng() + 0.5) / 4294967296.0; };
  int score = 0;
  for (auto &v : cl)
    score += costof(v);
  int best = score;
  auto bestcl = cl;
  for (int t = 0; t < steps; t++) {
    int i = rng() % c, j = rng() % c;
    if (i == j)
      continue;
    int x = rng() % cl[i].size(), y = rng() % cl[j].size(),
        old = costof(cl[i]) + costof(cl[j]);
    swap(cl[i][x], cl[j][y]);
    int nv = costof(cl[i]) + costof(cl[j]);
    double temp = 1.5 * pow(0.03 / 1.5, double(t) / steps);
    if ((baseof(cl[i]) & hm) && (baseof(cl[j]) & hm) &&
        (nv <= old || real() < exp((old - nv) / temp))) {
      score += nv - old;
      if (score < best) {
        best = score;
        bestcl = cl;
      }
    } else
      swap(cl[i][x], cl[j][y]);
  }
  cl = bestcl;
  vector<U> mask, black;
  vector<int> content;
  for (int j = h; j < 63; j++) {
    content.push_back(j);
    mask.push_back(U(1) << j);
    black.push_back(U(1) << j);
  }
  for (int j = 0; j < h; j++) {
    mask.push_back(U(1) << j);
    black.push_back(U(1) << j);
  }
  int ctrl[2] = {int(mask.size()), int(mask.size() + 1)};
  mask.push_back(hm | rescue);
  black.push_back(0);
  mask.push_back(hm | rescue);
  black.push_back(rescue);
  vector<int> member(p);
  for (auto &v : cl) {
    U base = baseof(v), handle = 0;
    vector<int> opts;
    for (int j = 0; j < h; j++)
      if (base >> j & 1)
        opts.push_back(j);
    shuffle(opts.begin(), opts.end(), rng);
    for (int z = 0; z < min(degree, int(opts.size())); z++)
      handle |= U(1) << opts[z];
    int item = mask.size();
    mask.push_back(cm | handle);
    black.push_back((base & cm) | handle);
    for (int a : v)
      member[a] = item;
  }
  if (int(mask.size()) != k) {
    cerr << "size fail\n";
    return 1;
  }
  for (int item = 0; item < k; item++) {
    string s(64, '.');
    for (int j = 0; j < 64; j++)
      if (mask[item] >> j & 1)
        s[j] = '0' + ((black[item] ^ flip) >> j & 1);
    cout << s << '\n';
  }
  cout.flush();
  vector<int> order(k);
  iota(order.begin(), order.end(), 0);
  int current = -1;
  long long stats[7] = {};
  for (int turn = 0; turn < r; turn++) {
    int a;
    if (!(cin >> a) || a < 0)
      return 0;
    U target = codes[a], ones = target & hm;
    int page = member[a];
    vector<pair<int, int>> out;
    auto move = [&](int item, int d) {
      auto it = find(order.begin(), order.end(), item);
      if (it == order.end()) {
        cerr << "notfound\n";
        exit(1);
      }
      order.erase(it);
      order.insert(order.begin() + d, item);
      out.emplace_back(item, d);
    };
    auto frontctrl = [&]() {
      return find(order.begin(), order.end(), ctrl[0]) <
                     find(order.begin(), order.end(), ctrl[1])
                 ? ctrl[0]
                 : ctrl[1];
    };
    if (current >= 0)
      move(current, ((mask[current] & hm) & ~ones) ? k - 1 : bn);
    stats[0] += out.size();
    int before = out.size();
    move(frontctrl(), k - 1);
    move(frontctrl(), k - 1);
    stats[1] += out.size() - before;
    before = out.size();
    vector<int> route;
    int depth = k;
    for (int j = 0; j < h; j++)
      if (mask[page] >> j & 1) {
        vector<int> path;
        for (int item : order) {
          if (item == page)
            break;
          if (mask[item] >> j & 1)
            path.push_back(item);
        }
        if (int(path.size()) < depth) {
          depth = path.size();
          route = path;
        }
      }
    for (int item : route) {
      if (keep_base && item >= bn && item < bn + h)
        move(item, find(order.begin(), order.end(), page) - order.begin());
      else
        move(item, k - 1);
    }
    stats[2] += out.size() - before;
    before = out.size();
    U patches = target & cm & ~black[page];
    vector<int> bank(order.begin(), order.begin() + bn);
    int val = pc(patches), bestcut = val, cut = 0;
    for (int t = 0; t < bn; t++) {
      U bit = U(1) << content[bank[t]];
      if (patches & bit)
        val--;
      else if (!(target & bit))
        val++;
      if (val < bestcut) {
        bestcut = val;
        cut = t + 1;
      }
    }
    int count = cut;
    for (int t = cut; t < bn; t++)
      if (patches >> content[bank[t]] & 1) {
        move(bank[t], 0);
        count++;
      }
    for (int t = 0; t < cut; t++)
      if (!(target >> content[bank[t]] & 1)) {
        move(bank[t], bn - 1);
        count--;
      }
    stats[3] += out.size() - before;
    before = out.size();
    move(page, count);
    current = page;
    stats[4] += out.size() - before;
    before = out.size();
    U secured = mask[page] & hm;
    int prefix = 0;
    for (int ix = bn + 1; ix < k; ix++) {
      int item = order[ix];
      if (item == ctrl[0] || item == ctrl[1] || ((mask[item] & hm) & ~ones))
        break;
      secured |= mask[item] & hm;
      prefix++;
    }
    while (ones & ~secured) {
      int pos[192];
      vector<vector<int>> lists(h);
      for (int ix = 0; ix < k; ix++) {
        int item = order[ix];
        pos[item] = ix;
        U z = mask[item] & hm;
        while (z) {
          int j = __builtin_ctzll(z);
          z &= z - 1;
          lists[j].push_back(item);
        }
      }
      int end = min(pos[ctrl[0]], pos[ctrl[1]]), chosen = -1, via = -1;
      double bestvalue = -1;
      int bestgain = -1, bestcost = 10000;
      for (int item = bn; item < k; item++)
        if (item != current && item != ctrl[0] && item != ctrl[1] &&
            pos[item] < end) {
          U bits = mask[item] & hm, gainbits = bits & ones & ~secured;
          if (!gainbits || (bits & ~ones))
            continue;
          int gain = pc(gainbits), dep = k, endpoint = -1;
          for (U z = gainbits; z; z &= z - 1) {
            int j = __builtin_ctzll(z);
            int rank =
                find(lists[j].begin(), lists[j].end(), item) - lists[j].begin();
            if (rank < dep) {
              dep = rank;
              endpoint = j;
            }
          }
          int cost = dep + 1;
          double value = double(gain) / pow(double(cost), ratio);
          if (value > bestvalue ||
              (value == bestvalue &&
               (gain > bestgain || (gain == bestgain && cost < bestcost)))) {
            bestvalue = value;
            bestgain = gain;
            bestcost = cost;
            chosen = item;
            via = endpoint;
          }
        }
      if (chosen < 0) {
        cerr << "coverage failure " << turn << "\n";
        return 1;
      }
      vector<int> path;
      for (int item : lists[via]) {
        if (item == chosen)
          break;
        path.push_back(item);
      }
      for (int item : path) {
        if (keep_base && item >= bn && item < bn + h)
          move(item, find(order.begin(), order.end(), chosen) - order.begin());
        else
          move(item, k - 1);
      }
      move(chosen, bn + 1);
      prefix++;
      secured |= mask[chosen] & hm;
    }
    stats[5] += out.size() - before;
    before = out.size();
    int desired = ctrl[bool(target & rescue)];
    if (frontctrl() != desired)
      move(frontctrl(), k - 1);
    move(desired, bn + 1 + prefix);
    stats[6] += out.size() - before;
    if (out.size() > 384) {
      cerr << "too many\n";
      return 1;
    }
    cout << out.size() << '\n';
    for (auto [item, d] : out)
      cout << item << ' ' << d << '\n';
    cout.flush();
  }
  cerr << "STATS";
  for (auto x : stats)
    cerr << " " << x;
  cerr << "\n";
}
