cookbook('Flour water salt yeast').


novel('The Guide').

fiction('Michael Storgoff').

dictionary('OED').
dictionary('Websters').
dictionary('Johnstons').


rel('The Guide', isa, novel).
rel('Flour water salt yeast', isa, cookbook).
rel('OED', isa, dictionary).
rel('Websters', isa, dictionary).
rel('Johnstons', isa, dictionary).
rel('Michael Storgoff', isa, fiction).


rel(novel, subset, fiction).
rel(fiction, subset, book).
rel(dictionary, subset, nonfiction).
rel(cookbook, subset, nonfiction).
rel(nonfiction, subset, book).

rel(X, isa, Z):-
        rel(Y, subset, Z),
        rel(X, isa, Y).
