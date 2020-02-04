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
rel(cookbook, subset, fiction).
rel(nonfiction, subset, book).


author('Websters','Noah').
author('Johnstons', 'Samuels').
author('Michael Storgoff', 'Jules').
author('The Guide', 'RK').

editor(X,Y):-
	rel(X, isa, book).

fiction(X,Y):-
	rel(X, isa, fiction).

volume('OED',20):-
	rel('OED', isa, book).

volume(X,Y):-
	not(X = 'OED'),
	rel(X, isa, book),
	Y = 1.

rel(X, isa, Z):-
	rel(Y, subset, Z),
	rel(X, isa, Y).


agrees(X,Y):-
	rel(X, isa, book),
	rel(Y, isa, book),
	(author(X,_),author(Y,_));(not(author(X,_)),not(author(Y,_)));(author(X,_),not(author(Y,_))),
	(volume(X,_),volume(Y,_));(not(volume(X,_)),not(volume(Y,_)));(volume(X,_),not(volume(Y,_))),
	(editor(X,_),editor(Y,_));(not(editor(X,_)),not(editor(Y,_)));(editor(X,_),not(editor(Y,_))).

