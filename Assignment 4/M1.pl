fiction(michealstrogoff).
fiction(X) :- novel(X).
novel(the_guide).
nonfiction(X) :- dictionary(X) ; cookbook(X).
cookbook(flour_water_salt_yeast).
dictionary(oed).
dictionary(webster).
dictionary(johnston).
book(X) :- fiction(X) ; nonfiction(X).
