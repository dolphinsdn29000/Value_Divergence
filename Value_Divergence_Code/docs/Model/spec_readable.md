# Two-Task Cobb–Douglas Team (Markdown recreation)


<!-- Page 1 -->

Two-Task Cobb–Douglas Team with Comparative Advantage:
Equilibrium Taxonomy, Impossibility Results, and Parameter
Regions
1
Model
Two players i ∈ {1, 2} supply nonnegative efforts xi, yi ≥ 0 on tasks X and Y . Aggregate outputs
are linear in efforts with productivity (benefit-side comparative advantage)
X = p1xx1 + p2xx2,
Y = p1yy1 + p2yy2,
pix, piy > 0.
Preferences are Cobb–Douglas; costs are quadratic in own total effort:
Ui(xi, yi; x−i, y−i) = X 1−ai Y ai − ci
2 (xi + yi)2,
ai ∈ (0, 1), ci > 0.
Let
r ≡ Y
X > 0,
ri ≡
ai piy
(1 − ai) pix
(i = 1, 2).
When player i is interior (xi > 0 and yi > 0), first-order conditions imply r = ri.
For later use, define the total effort if player i acts as:
X-only:
sX
i (r) = (1 − ai) pix
ci
rai,
Y-only:
sY
i (r) = ai piy
ci
r−(1−ai).
(1)
2
KKT (complementarity) conditions
Write si = xi + yi. For each choice variable we have the complementary slackness:
xi ≥ 0,
c1s1 − (1 − a1)p1xra1 ≥ 0,
x1 ·
�
c1s1 − (1 − a1)p1xra1�
= 0,
yi ≥ 0,
c1s1 − a1p1yra1−1 ≥ 0,
y1 ·
�
c1s1 − a1p1yra1−1�
= 0,
and analogously for player 2 with c2, p2x, p2y, a2. Cobb–Douglas requires X > 0 and Y > 0 (since
ai ∈ (0, 1)), so any equilibrium must deliver strictly positive X, Y .
3
From 16 support masks to 7 feasible patterns
A support mask is m = (mx1, my1, mx2, my2) ∈ {0, 1}4, where mx1 = 1 means x1 > 0, etc. There
are 24 = 16 masks.
Lemma 1 (Immediate impossibilities). Fix ai ∈ (0, 1) and pix, piy, ci > 0. At any equilibrium:
1


<!-- Page 2 -->

(a) For each player i, it is impossible that xi = yi = 0. (Because for any finite r > 0, both
marginal benefits are strictly positive, violating complementary slackness.)
(b) It is impossible that both players choose only X (my1 = my2 = 0), because Y = 0 contradicts
Cobb–Douglas.
(c) It is impossible that both players choose only Y (mx1 = mx2 = 0), because X = 0.
As a result, the only admissible economic patterns are obtained by classifying each player as:
B (interior): (xi > 0, yi > 0),
X-only: (xi > 0, yi = 0),
Y-only: (xi = 0, yi > 0),
which yields 3 × 3 = 9 patterns. By Lemma 1(b,c) two are infeasible (X,X) and (Y,Y) at the pair
level, leaving the following seven feasible patterns:
(B, B), (X, Y ), (Y, X), (B, X), (X, B), (B, Y ), (Y, B).
4
Closed-form ratios and efforts for the seven feasible patterns
Define the two useful constants
KXY ≡
a2 p2
2y c1
(1 − a1) p2
1x c2
,
KY X ≡
a1 p2
1y c2
(1 − a2) p2
2x c1
.
The exponents 2 + a1 − a2 and 2 + a2 − a1 lie in (1, 3) since ai ∈ (0, 1).
(A) Both interior: (B,B)
Interior FOCs for both players imply r = r1 = r2. Given any r with r1 = r2, totals are
s1 = (1 − a1)p1x
c1
ra1 = a1p1y
c1
r−(1−a1),
s2 = (1 − a2)p2x
c2
ra2 = a2p2y
c2
r−(1−a2).
Feasibility Y = rX determines only a line of splits (y1, y2) within the box 0 ≤ yi ≤ si, hence a
continuum of equilibria.
(B) Full specialization: (X,Y)
Player 1 is X-only, player 2 is Y-only. Aggregation and FOCs imply the scalar equation
r 2+a1−a2 = KXY
⇒
r = K
1
2+a1−a2
XY
.
Totals are s1 = sX
1 (r), s2 = sY
2 (r) from (1). The realized allocation is
(x1, y1; x2, y2) = (s1, 0; 0, s2).
(C) Full specialization: (Y,X)
Symmetrically,
r 2+a2−a1 = KY X
⇒
r = K
1
2+a2−a1
Y X
,
(x1, y1; x2, y2) = (0, s1; s2, 0),
with s1 = sY
1 (r), s2 = sX
2 (r).
2


<!-- Page 3 -->

(D) One interior, one specialist: (B,Y)
Here r = r1 (player 1 interior). Player 2 is Y-only, so X initially comes only from player 1 and Y
from both. Let
Xbase = 0,
Ybase = p2y s2
with s2 = sY
2 (r).
Player 1 total is s1 = sX
1 (r) = sY
1 (r) at r = r1. Feasibility Y = rX pins player 1’s split by solving
p1yy1 = r · p1x(s1 − y1) − Ybase
⇒
y1 = r p1xs1 − Ybase
p1y + r p1x
,
x1 = s1 − y1.
This split is feasible iff 0 ≤ y1 ≤ s1. That inequality reduces to the single capacity condition
r 2+a1−a2
1
≥ KXY
(together with the consistency r1 ≤ r2).
(E) One interior, one specialist: (Y,B)
Here r = r2, player 1 is Y-only with s1 = sY
1 (r), and player 2 is interior with s2 = sX
2 (r) = sY
2 (r).
Solving Y = rX for y2 gives
y2 = r p2xs2 − Ybase
p2y + r p2x
,
x2 = s2 − y2,
Ybase = p1ys1.
Feasibility 0 ≤ y2 ≤ s2 reduces to
r 2+a2−a1
2
≥ KY X
(with consistency r2 ≤ r1).
(F) One interior, one specialist: (B,X)
Here r = r1, player 2 is X-only with s2 = sX
2 (r).
Feasibility determines y1 as in (B,Y), and
0 ≤ y1 ≤ s1 reduces to the dual capacity bound
r 1+a2−a1
1
≤ (1 − a1) p1y p1x c2
(1 − a2) p2
2x c1
(with consistency r1 ≥ r2).
(G) One interior, one specialist: (X,B)
Here r = r2, player 1 is X-only with s1 = sX
1 (r); solving gives the dual bound
r 1+a1−a2
2
≤ (1 − a2) p2y p2x c1
(1 − a1) p2
1x c2
(with consistency r2 ≥ r1).
Notes.
(i) The (B,B) case produces a continuum of equilibria (a line segment of splits) whenever
r1 = r2. (ii) The (X,Y), (Y,X) cases deliver a unique r and unique efforts. (iii) In the mixed (B,·)
cases, the total si is pinned and the split is uniquely pinned by feasibility; the capacity inequalities
above are exactly the algebraic form of 0 ≤ yi ≤ si.
3


<!-- Page 4 -->

5
Parameter regions and uniqueness
Collect the consistency conditions and capacity inequalities:
(X,Y): r = K1/(2+a1−a2)
XY
and r ∈ [r1, r2].
(Y,X): r = K1/(2+a2−a1)
Y X
and r ∈ [r2, r1].
(B,Y): r = r1,
r1 ≤ r2,
r2+a1−a2
1
≥ KXY .
(Y,B): r = r2,
r2 ≤ r1,
r2+a2−a1
2
≥ KY X.
(B,X): r = r1,
r1 ≥ r2,
r1+a2−a1
1
≤ (1 − a1)p1yp1xc2
(1 − a2)p2
2xc1
.
(X,B): r = r2,
r2 ≥ r1,
r1+a1−a2
2
≤ (1 − a2)p2yp2xc1
(1 − a1)p2
1xc2
.
(B,B): r1 = r2 (knife-edge); a continuum of splits.
Proposition 1 (Generic uniqueness). For almost every parameter vector (a1, a2, p1x, p1y, p2x, p2y, c1, c2)
(i.e. away from the equalities that define the region boundaries), exactly one of the seven sets above
holds, and the resulting equilibrium effort vector is unique. Multiple patterns can be feasible only on
knife-edges (e.g. r1 = r2 or when the specialized ratio equals a threshold), and there the allocations
coincide or form a one-dimensional continuum as in (B,B).
6
Feasibility of the 16 support masks (exhaustive)
Let m = (mx1, my1, mx2, my2) ∈ {0, 1}4 indicate positivity of (x1, y1, x2, y2). Table 1 lists all masks
and their status. “Type” maps each player’s support to {X, Y, B}. Impossibilities follow from
Lemma 1; all feasible masks fall into one of the seven patterns.
mask
P1 type
P2 type
feasible?
reason / pattern
0000
–
–
no
player 1 violates KKT; player 2 violates KKT
0001
Y
–
no
player 2 violates KKT (x2 = y2 = 0)
0010
X
–
no
player 2 violates KKT (x2 = y2 = 0)
0011
X
Y
yes
(X, Y )
0100
Y
–
no
player 2 violates KKT
0101
Y
Y
no
X = 0 impossible
0110
B
X
yes
(B, X)
0111
B
B
yes
(B, B) if r1 = r2; else no
1000
X
–
no
player 2 violates KKT
1001
X
Y
yes
(X, Y )
1010
X
X
no
Y = 0 impossible
1011
X
B
yes
(X, B)
1100
B
–
no
player 2 violates KKT
1101
B
Y
yes
(B, Y )
1110
B
X
yes
(B, X)
1111
B
B
yes
(B, B) if r1 = r2; else no
Table 1: All 16 support masks. Only the seven listed patterns are ever feasible.
4


<!-- Page 5 -->

7
Summary: which equation is used when (complete chart)
Pattern
Equilibrium ratio r
Consistency (threshold order)
Extra (capacity) condition
(X, Y )
r = K1/(2+a1−a2)
XY
r ∈ [r1, r2]
none
(Y, X)
r = K1/(2+a2−a1)
Y X
r ∈ [r2, r1]
none
(B, Y )
r = r1
r1 ≤ r2
r2+a1−a2
1
≥ KXY
(Y, B)
r = r2
r2 ≤ r1
r2+a2−a1
2
≥ KY X
(B, X)
r = r1
r1 ≥ r2
r1+a2−a1
1
≤ (1 − a1)p1yp1xc2
(1 − a2)p2
2xc1
(X, B)
r = r2
r2 ≥ r1
r1+a1−a2
2
≤ (1 − a2)p2yp2xc1
(1 − a1)p2
1xc2
(B, B)
r = r1 = r2
equality
continuum of splits
Table 2: Complete mapping from parameters to the equation used. Away from the boundary
equalities, exactly one row applies and the equilibrium effort vector is unique.
Derivation notes (capacity inequalities).
In the mixed (B,·) cases the interior player has
total si fixed by r; feasibility Y = rX pins their split via (piy + rpix) yi = r
�
Xbase + pixsi
�
− Ybase.
Requiring 0 ≤ yi ≤ si reduces to the power inequalities reported above after substituting sX
i , sY
i
from (1) and simplifying.
5
