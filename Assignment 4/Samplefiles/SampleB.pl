% Assignment 4 Problem 3 Sample Problem Code B.
% CSC 520 F 2019
% Dr. Lynch


duration(a, 10).
duration(b, 5).
duration(c, 5).
duration(d, 9).
duration(e, 21).
duration(f, 16).
duration(g, 21).
duration(h, 12).
duration(i, 10).
duration(j, 25).
duration(k, 35).
duration(l, 8).
duration(m, 4).
duration(n, 5).


prerequisite(b, a).
prerequisite(c, b).
prerequisite(d, c).
prerequisite(e, c).
prerequisite(f, e).
prerequisite(h, d).
prerequisite(g, f).
prerequisite(f, h).
prerequisite(i, a).
prerequisite(j, i).
prerequisite(k, j).
prerequisite(l, a).
prerequisite(m, l).
prerequisite(n, m).
prerequisite(j, n).
prerequisite(g, k).
