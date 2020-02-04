from copy import deepcopy
import queue
import json
import time
import sys


class QueenGraph:

    """
    @:parameter n: No. of queens, no. of columns and no. of rows
    @
    """

    def __init__(self, n, constraint_file, result_file):

        """
        :param n: No of queen
        :param constraint_file: CFile Param
        :param result_file: RFile Param
        """

        # N value
        self._n = n

        # CFile
        self._constraint_file = constraint_file

        # RFile
        self._result_file = result_file

        # Queengraph attribute that hold the variable and possible domain values
        self._variables = dict()

        # This value is not used, can be ignored
        self._values = None

        # initialize the variables and their initial domain values
        self._set_variables_domain_values()

        # initialize assignments --> initially empty
        self._assignments = []

        # generate CFile
        self._generate_cfile()

        # start time of the algorithm
        self._start_time = time.time()

        # end time of the algorithm
        self._end_time = None

        # time take for the call to one of the algorithm to finish
        self._time_taken = None

        self._backtrack_steps_count = 0

    def _set_time_taken(self):

        if self._end_time is None:
            raise ValueError("End time has not been set.")
        else:
            self._time_taken = self._end_time - self._start_time

    def _generate_cfile(self):

        cfilestring = "Both the MAC and Forward Checking algorithm consider row value for each column as variable.\n"
        cfilestring += "Hence, every column is a variable and the domain values are the possible row assignment " \
                       "of queen to each column.\n"

        cfilestring += "======\n"
        cfilestring += "N = {0}\n".format(self._n)

        cfilestring += "===================\n"
        cfilestring += "Variable and Domain\n"
        cfilestring += "===================\n"

        for key in sorted(self._variables):
            variable_domain = "Variable {0} (Column {1}): Domain Values: {2} (Possible rows to place queen at for " \
                              "column or variable {3})\n"\
                .format(key, key, self._variables[key], key)

            cfilestring += variable_domain

        cfilestring += "\n=============================================================================" \
                       "=========================================\n"
        cfilestring += "Constraint per variable with a valid domain value in a matrix representing binary contraint " \
                       "with every other variable.\n"
        cfilestring += "\n=============================================================================" \
                       "=========================================\n"

        cfilestring += "Example to understand constraint representation\n"
        cfilestring += "==================================================\n"

        cfilestring += "When Queen for (Variable) Column 4 is placed at row 4\n!Q1  Q2  Q3  X  \n" \
                       "Q1  !Q2  Q3  X  \nQ1  Q2  !Q3  X  \n!Q1  !Q2  !Q3  Q4 " \
                       "\n{1: [2, 3], 2: [1, 3], 3: [1, 2], 4: [4]}\n"

        cfilestring += "This means Variable 4 is assigned a value 4 (Represented by Q4).\n"
        cfilestring += "!Qx means Queen can't be at that row for column x.\n"
        cfilestring += "X represent that the particular variable has been assigned a domain value and " \
                       "other values can't be taken by that variable.\n\n"
        cfilestring += "Internal representation: {1: [2, 3], 2: [1, 3], 3: [1, 2], 4: [4]}\n"
        cfilestring += "Since variable 4 is assigned value 4, other values become inconsistent and not applicable,\n" \
                       "hence 4: [4]. 1:[2,3] implies when Queen for variable 4 is at row 4, then the binary\n" \
                       "constraint for variable 1 with 4 says variable 1 can only take values  2 and 3, " \
                       "hence 1: [2,3].\n"
        cfilestring += "=============================================================================" \
                       "===============================================\n"

        cfilestring += "Constraints\n"
        cfilestring += "============\n"

        for key in sorted(self._variables):
            for value in self._variables[key]:

                p_variables = deepcopy(self._variables)
                p_variables[key] = []
                p_variables[key].append(value)

                cfilestring += "When Queen for (Variable) Column {0} is placed at row {1}\n".format(key, value)

                mat = []
                for i in range(self._n):
                    mat.append(['X  '] * self._n)

                mat[value-1][key-1] = "Q{0} ".format(key)

                for otherkey in sorted(self._variables):
                    for othervalue in self._variables[otherkey]:
                        if key != otherkey:
                            if QueenGraph.check_constraint_for_two_queens(value, key, othervalue, otherkey):
                                mat[othervalue-1][otherkey-1] = "!Q{0} ".format(otherkey)
                                p_variables[otherkey].remove(othervalue)
                            else:
                                mat[othervalue-1][otherkey-1] = "Q{0} ".format(otherkey)

                current_matrix = ""
                for v in mat:
                    current_matrix = current_matrix + " ".join(v)+"\n"
                cfilestring += current_matrix
                cfilestring += "Internal constraint representation: "
                cfilestring += (str(p_variables) + "\n\n")

        fp = open(self._constraint_file, 'w+')
        fp.write(cfilestring)
        fp.close()

    def _generate_r_file(self):

        output_string = ""
        output_string += "===============================================\n"
        output_string += "N = {0}\n".format(self._n)
        output_string += "===============================================\n\n"

        for result in self._assignments:
            board = []

            for i in range(self._n):
                board.append(["X"]*self._n)

            for key in result:
                board[result[key]-1][int(key)-1] = "Q"

            for column in board:
                output_string = output_string + "\t".join(column) + "\n"

            output_string += ("\nInternal representation of result: " + str(result) + "\n")

            output_string += "\n==================\n\n"

        if self._time_taken is None:
            self._time_taken = 0
        output_string += "\nTime take: {0} secs\n".format(self._time_taken)
        output_string += "Backtracking counts: {0}\n".format(self._backtrack_steps_count)

        f = open(self._result_file, 'w+')
        f.write(output_string)
        f.close()

    def _set_variables_domain_values(self):

        # initializing variable and domain values

        for i in range(1, self._n+1):

            self._variables[i] = []
            for j in range(1, self._n+1):
                self._variables[i].append(j)

    @staticmethod
    def check_constraint_for_two_queens(i1, j1, i2, j2):

        """

        :param i1: row value for queen 1
        :param j1: column value for queen 1
        :param i2: row value for queen 2
        :param j2: column value for queen 2
        :return: Returns true, if the constraint fails between arc
        """

        # checking for diagonal with (abs(j1-j2)/abs(i1-i2) == 1 and row column as usual
        return (i1 == i2) or (j1 == j2) or (abs(j1-j2)/abs(i1-i2) == 1)

    @staticmethod
    def cmp(a, b):
        return (a > b) - (a < b)

    def run_forward_chaining(self):

        # initial variable to start with
        start_state_domain_values = self._variables[1]

        for domain_value in start_state_domain_values:
            value_domain_map = deepcopy(self._variables)
            # running forward chaining on each domain value for first variable
            self._forward_chain(value_domain_map=value_domain_map, assignment_map={1: domain_value},
                                selection_key=1, selection_value=domain_value, level=1)

        self._generate_r_file()

    def _forward_chain(self, value_domain_map, assignment_map, selection_key, selection_value, level):

        """

        :param value_domain_map: value domain map at this level of the recursion call
        :param assignment_map: assignment map at this level of the recursion call
        :param selection_key: selected variable at this level, which is to be checked
        :param selection_value: selected value for the selected variable, which is to be checked
        for consistencies and other things as part of algorithms
        :param level: for debug reference, level of the recursion tree
        :return: None
        """

        # stop when the solution count = 2*n
        if len(self._assignments) >= 2*self._n:
            return

        # if the assignment is full and satisfying add to the final assignment
        if len(assignment_map) == self._n:
            self._assignments.append(assignment_map)
            if len(self._assignments) == 2*self._n:
                self._end_time = time.time()
                self._set_time_taken()
            return

        # remove selected value from the domain of all the variables
        for key in value_domain_map:
            try:
                value_domain_map[key].remove(selection_value)
            except ValueError:
                pass

        # for all the neighbors for selected variable
        for key in value_domain_map:
            if key != selection_key:
                domain_of_other_variable = value_domain_map[key]
                values_to_be_removed = []
                # removing inconsistent values from neighbors for the selected assignment of the variable
                for domain_ele_of_other_variable in domain_of_other_variable:

                    if QueenGraph.check_constraint_for_two_queens(selection_value, level,
                                                                  domain_ele_of_other_variable, key):

                        values_to_be_removed.append(domain_ele_of_other_variable)

                # removing values from neighbors domain
                for values in values_to_be_removed:
                    value_domain_map[key].remove(values)

        # applying smallest domain heuristic
        smallest = 9999
        next_explore_key = None

        for key in value_domain_map:
            if key not in assignment_map and key != level:
                len_domain = len(value_domain_map[key])
                if len_domain < smallest:
                    smallest = len_domain
                    next_explore_key = key

        # if some domain has exhausted
        if smallest == 0:
            self._backtrack_steps_count += 1
            return
        if next_explore_key is None:
            self._backtrack_steps_count += 1
            return

        # choose variable with smallest domain and do forward chaining
        for value in value_domain_map[next_explore_key]:
            v_map = deepcopy(value_domain_map)
            del v_map[selection_key]
            as_map = deepcopy(assignment_map)
            as_map[next_explore_key] = value
            self._forward_chain(value_domain_map=v_map, assignment_map=as_map, selection_key=next_explore_key,
                                selection_value=value, level=level+1)

    @staticmethod
    def revised(xi, xj, value_map):

        """
        :param xi: Tuple, having variable, assigned value for xi
        :param xj: Tuple, having variable, assigned value for xj
        :param value_map: map of variable and domain ( or reduced domain as algorithm continues )
        :return: True, if xi domain is reduced else false
        """

        revised = False

        # for the value in the domain of xi
        for value in value_map[xi]:
            domain_of_xj = value_map[xj]
            not_matching_count = 0
            for domain_of_xj_value in domain_of_xj:
                if QueenGraph.check_constraint_for_two_queens(value, xi, domain_of_xj_value, xj):
                    not_matching_count += 1

            # if no value satisfies select xi value in xj, remove it from domain of xi
            if not_matching_count == len(domain_of_xj):
                value_map[xi].remove(value)
                revised = True

        return revised

    def single_arc_ac3(self, xi, xj, value_map):

        """
        :param xi: Arc i
        :param xj: Arc j
        :param value_map: Variable domain map
        :return: Returns true, if after ac3 inference, there are no inconsistencies found
        """

        # insert the received arc to the queue
        q = queue.Queue(maxsize=0)
        q.put((xi, xj))

        # loop for ac3 as defined in the text book
        while not q.empty():
            q_value = q.get()
            xI, xJ = q_value[0], q_value[1]
            if self.revised(xI, xJ, value_map):
                if len(value_map[xI]) == 0:
                    return False
                for i in range(1, self._n+1):
                    if i != xJ and i != xI:
                        q.put((i, xI))
        return True

    def _generate_unique_assignment_for_mac(self):

        """
        Generates only unique solution and add them to the final list
        :return: None
        """

        tmp = set()

        for x in self._assignments:
            z = json.dumps(x, sort_keys=True)
            tmp.add(z)

        self._assignments = []
        for z in tmp:
            self._assignments.append(json.loads(z))

    def run_mac(self):
        # start the backtrack
        self.mac_backtrack({}, self._variables, 1)
        self._end_time = time.time()
        self._set_time_taken()
        self._generate_r_file()

    def mac_backtrack(self, assignment, var_value_map, level):

        """
        :param assignment: Assignment map state at this level of recursion call
        :param var_value_map: Variable domain map
        :param level: Debug param for checking level of recursion
        :return: Returns true is an assignment is consistent else not
        """

        self._backtrack_steps_count += 1

        # if len(self._assignments) >= 2*self._n:
        #     return
        var = None
        # select the first unassigned variable
        for key in var_value_map:
            var = key
            break

        # select one value at a time from the domain of the selected variable
        for value in var_value_map[var]:
            # checking if value is consistent with assignment
            for k in assignment:
                if QueenGraph.check_constraint_for_two_queens(assignment[k], k, value, var):
                    break
            else:
                # if the value is consistent with the assignment
                for key in self._variables:
                    if key not in assignment and key != var:

                        # run the inference of ac3 on the assignment
                        inference = self.single_arc_ac3(key, var, var_value_map)

                        # if the inference is true, then add the assignment to the assignment map
                        if inference:

                            assignment[var] = value
                            v_map = deepcopy(var_value_map)
                            del v_map[var]

                            # call the backtrack for the remaining unassigned variables
                            result = self.mac_backtrack(assignment, v_map, level + 1)

                            if result:
                                return result

                    # because of the implementation chosen, the check for the len(assignment) == N is done here
                    elif key not in assignment and len(assignment) == self._n-1:

                        # for the last assignment, check if the remaining domain values for the remaining unassigned
                        # variable are consistent with the current assignment, and if true add it to the assignment
                        for val in var_value_map[var]:
                            for k in assignment:
                                if QueenGraph.check_constraint_for_two_queens(val, var, assignment[k], k):
                                    break
                            else:
                                assignment[var] = val
                                self._assignments.append(deepcopy(assignment))
                                self._generate_unique_assignment_for_mac()
                                if len(self._assignments) == 2 * self._n:
                                    self._end_time = time.time()
                                    self._set_time_taken()

                                    self._generate_r_file()
                                    exit(1)

                                del assignment[var]
            if var in assignment:
                del assignment[var]

        return False


if len(sys.argv) < 5 or len(sys.argv) > 5:
    raise ValueError("Invalid number of arguments.")
else:

    algo = sys.argv[1]

    if algo != "MAC" and algo != "FOR":
        raise ValueError("Invalid algorithm specified.")

    try:
        n = int(sys.argv[2])
    except ValueError:
        raise ValueError("Invalid value for N.")

    c_file = sys.argv[3]
    r_file = sys.argv[4]

    x = QueenGraph(n=n, constraint_file=c_file, result_file=r_file)

    if algo == "FOR":
        x.run_forward_chaining()
    elif algo == "MAC":
        x.run_mac()
