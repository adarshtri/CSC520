% Assignment 4 Problem 3 Sample Problem Code A.
% CSC 520 F 2019
% Dr. Lynch


duration(a, 10).
duration(b, 20).
duration(c, 20).
duration(e, 35).
duration(d, 10).

prerequisite(b, a).
prerequisite(c, b).
prerequisite(e, a).
prerequisite(d, c).
prerequisite(d, e).
