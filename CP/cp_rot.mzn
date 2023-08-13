include "diffn.mzn";
include "cumulative.mzn";

% INPUT VARIABLES

% width of the plate
int: w;
% n. of circuits
int: n;
set of int: CIRCUITS = 1..n;
% width of all the cirdcuits
array[CIRCUITS] of int: widths;
% height of all the cirdcuits
array[CIRCUITS] of int: heights;

% if a circuit is rotated
array[CIRCUITS] of var bool: rotate;

% bounds to the final height to reduce the search space
int: min_h = min(max(heights), max(widths));
int: max_h = sum(heights);

% OUTPUT VARIABLES

% final height
var min_h..max_h: h = max([Y[i]+heights_upd[i] | i in CIRCUITS]);  
% X and Y coordinates of all the circuits in the plate
array[CIRCUITS] of var 0..w - min(widths): X; 
array[CIRCUITS] of var 0..max_h - min(heights): Y;

array [CIRCUITS] of var int: widths_upd = [if rotate[i] then heights[i] else widths[i] endif | i in CIRCUITS];
array [CIRCUITS] of var int: heights_upd = [if rotate[i] then widths[i] else heights[i] endif | i in CIRCUITS];

% CONSTRAINTS

% constraint to not exceed max width and height
constraint max([X[i] + widths_upd[i] | i in CIRCUITS]) <= w;
constraint max([Y[i] + heights_upd[i] | i in CIRCUITS]) <= max_h;
% to avoid overlapping among circuits
constraint diffn(X, Y, widths_upd, heights_upd);

constraint cumulative(Y, heights_upd, widths_upd, w);
constraint cumulative(X, widths_upd, heights_upd, h);
% don't rotatae if circuit is a square
constraint forall(i in CIRCUITS)(if widths[i] == heights[i] then rotate[i]=false endif);


solve :: seq_search([
            int_search([h], smallest, indomain_min),
            int_search(X, first_fail, indomain_min),
            int_search(Y, first_fail, indomain_min)])
      minimize h;