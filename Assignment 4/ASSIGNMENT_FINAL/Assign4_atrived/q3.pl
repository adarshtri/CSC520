
maximum([F|R],Z) :- max(R,F,Z).

max([],Z,Z).

max([[P,L]|R],[_,Z],Max) :- L > Z, !, max(R,[P,L],Max).

max([_|R],Z,Max) :- max(R,Z,Max).

minimum([F|R],Z) :- min(R,F,Z).

min([],Z,Z).

min([[P,L]|R],[_,Z],Min) :- L < Z, !, min(R,[P,L],Min).

min([_|R],Z,Min) :- min(R,Z,Min).


%backward check traverse base predicate
backpass(C,[C],W):-
    earlyFinish(C,W),
    not(prerequisite(PQ,C)).

%backward checking recursive predicate
backpass(C,[C|P],TIME):-
    prerequisite(PQ,C),
    duration(PQ,TIME1),
    backpass(PQ,P,TIME2),
    TIME is TIME2-TIME1.


%forward checking traverse base condition
forwardpass(C,[C],TIME):-
    duration(C,TIME),
    not(prerequisite(C,PQ)).

%forward checking traverse recursive predicate match
forwardpass(C,[C|P],TIME):-
    duration(C,TIME1),
    prerequisite(C,PQ),
    forwardpass(PQ,P,TIME2),
    TIME is TIME1+TIME2.

%earlyFinish Predicate
earlyFinish(T,TM):-
    setof([A,B],forwardpass(T,A,B),Set),
    Set = [_|_],
    maximum(Set,[P,TM]).

%max slack predicate
maxSlack(TASK,TIME):-
    earlyFinish(TASK,EarlyFinish),
    duration(TASK,TaskDuration),
    EarlyStart is EarlyFinish-TaskDuration,
    lateStart(TASK,LateStart),
    TIME is LateStart-EarlyStart.


%criticalPath Predicate
criticalPath(TASK,PATH):-
    setof([X,Y],forwardpass(TASK,X,Y),Set),
    Set = [_|_],
    maximum(Set,[PATH,Length]).

%lateStart Predicate
lateStart(T,TM):-
    setof([A,B],backpass(T,A,B),Set),
    Set = [_|_],
    minimum(Set,[P,A]),
    duration(T,B),
    TM is A-B.
