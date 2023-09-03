include "diffn.mzn";
include "cumulative.mzn";
include "lex_lesseq.mzn";

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

% bounds to the final height to reduce the search space
int: min_h = ceil(sum(i in CIRCUITS)(widths[i]*heights[i]) / w);
int: max_h = sum(heights);

% OUTPUT VARIABLES

% final height
var min_h..max_h: h = max([Y[i]+heights[i] | i in CIRCUITS]);  
% X and Y coordinates of all the circuits in the plate
array[CIRCUITS] of var 0..w - min(widths): X; 
array[CIRCUITS] of var 0..max_h - min(heights): Y;

% CONSTRAINTS

% constraint to not exceed max width and height
constraint max([X[i] + widths[i] | i in CIRCUITS]) <= w;
constraint max([Y[i] + heights[i] | i in CIRCUITS]) <= h;
% to avoid overlapping among circuits
constraint diffn(X, Y, widths, heights);

constraint cumulative(Y, heights, widths, w);
constraint cumulative(X, widths, heights, h);

% symmetry breaking 

% for circuits with same height and width
constraint forall(i, j in CIRCUITS where i < j /\ widths[i]==widths[j] /\ heights[i]==heights[j])
      (lex_lesseq([X[i], Y[i]], [X[j],Y[j]]));
% horizontal symmetry

constraint lex_lesseq([X[i]| i in CIRCUITS],[w-X[i]-widths[i]|i in CIRCUITS]);
% verrtical flip
constraint lex_lesseq([Y[i]| i in CIRCUITS],[h-Y[i]-heights[i]|i in CIRCUITS]);



solve :: seq_search([
            int_search([h], smallest, indomain_min),
            int_search(X, input_order, indomain_min),
            int_search(Y, input_order, indomain_min),
            restart_constant(3000)])
      minimize h;