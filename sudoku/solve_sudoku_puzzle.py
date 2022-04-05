import copy
import queue


def read_file_to_lines(file_name):
    """
    Read every line in file
    Args:
        file_name:file path
    Return:
        every line in file
    """
    with open(file_name, "r") as file:
        lines = file.readlines()
    return lines


def cross_product(set1, set2):
    """
    cross product of two sets
    Args:
        set1:first set
        set2:second set
    Return:
        cross product of two sets
    """
    results = []
    for ele1 in set1:
        for ele2 in set2:
            results.append(ele1 + ele2)
    return results


row_flag_str = "ABCDEFGHI"
column_flag_str = "123456789"
digits_str = "123456789"

grid_names = cross_product(row_flag_str, column_flag_str)


class CSP:
    """
    Constraint satisfaction Problem
    """

    def __init__(self, domain=digits_str, grid=""):
        self.variables = grid_names
        self.domain = self.init_domain(grid)
        self.values = copy.deepcopy(self.domain)

        self.unitlist = (
            [cross_product(row_flag_str, c) for c in column_flag_str]
            + [cross_product(r, column_flag_str) for r in row_flag_str]
            + [cross_product(rs, cs) for rs in ("ABC", "DEF", "GHI") for cs in ("123", "456", "789")]
        )
        self.units = dict((s, [u for u in self.unitlist if s in u]) for s in grid_names)
        self.peers = dict((s, set(sum(self.units[s], [])) - set([s])) for s in grid_names)
        self.constraints = {(variable, peer) for variable in self.variables for peer in self.peers[variable]}

    def init_domain(self, grids):
        """
        init domains
        Args:
            grids:sudokus grids
        Return:
            Sudokus domains
        """
        index = 0
        domains = dict()
        for grid in self.variables:
            if grids[index] != "0":
                domains[grid] = grids[index]
            else:
                domains[grid] = digits_str
            index = index + 1
        return domains

    def is_end(self):
        """
        judge if end
        Return:
            if is end,return True,otherwise return False
        """
        for name in grid_names:
            if len(self.values[name]) > 1:
                return False
        return True


def print_grids(values):
    output = ""
    for variable in grid_names:
        output = output + values[variable]
    return output


def ac_3(csp):
    """
    Main AC-3 algorithm 
    """
    print("*************start ac-3**************88")
    ac_3_queue = queue.Queue()
    for constraint in csp.constraints:
        ac_3_queue.put(constraint)
    step = 0
    while not ac_3_queue.empty():
        (constraint_0, constraint_1) = ac_3_queue.get()
        if revise(csp, constraint_0, constraint_1):
            if len(csp.values[constraint_0]) == 0:
                return False
            for intersection_point in csp.peers[constraint_0] - set(constraint_1):
                ac_3_queue.put((intersection_point, constraint_0))
        step += 1
        print(f"step {step} queue length is {ac_3_queue.qsize()}")

    return True


def revise(csp, constraint_0, constraint_1):
    """
    Working of the revise algorithm
    Args:
        csp:Constraint satisfaction Problem
        constraint_0:constraint
        constraint_1:constraint
    """
    revised = False
    values = set(csp.values[constraint_0])
    for x in values:
        if not is_consistent(csp, x, constraint_0, constraint_1):
            csp.values[constraint_0] = csp.values[constraint_0].replace(x, "")
            revised = True
    return revised


def is_consistent(csp, constraint, constraint_0, constraint_1):
    """
    judge if the given assignment is consistent
    """
    for value in csp.values[constraint_1]:
        if constraint_1 in csp.peers[constraint_0] and value != constraint:
            return True
    return False


def display(values):
    """
    Display sudoku
    """
    for r in row_flag_str:
        if r in "DG":
            print("------------------------------------------------------------------------------")
        for c in column_flag_str:
            if c in "47":
                print(" | ", values[r + c], " ", end=" ")
            else:
                print(values[r + c], " ", end=" ")
        print(end="\n")


def display_line(line, row=9, column=9):
    for i in range(row):
        if i == 3 or i == 6:
            print("------------------------------------------------------------------------------")
        for j in range(column):
            if j == 3 or j == 6:
                print(" | ", line[i * row + j], " ", end=" ")
            print(line[i * row + j], " ", end=" ")
        print()


def back_track_search(csp):
    """
    back track search initializes the initial assignment and call the back track function
    Args:
        csp:Constraint satisfaction Problem
    """
    return back_track({}, csp)


def back_track(assignment, csp):
    if is_complete(assignment):
        return assignment

    var = select_unassigned_variables(assignment, csp)
    domain = copy.deepcopy(csp.values)

    for value in csp.values[var]:
        if is_consistent_back_track(var, value, assignment, csp):
            assignment[var] = value
            inferences = {}
            inferences = inference(assignment, inferences, csp, var, value)
            if inferences != "False":
                result = back_track(assignment, csp)
                if result != "False":
                    return result

            del assignment[var]
            csp.values.update(domain)
    return "False"


def inference(assignment, inferences, csp, var, value):
    inferences[var] = value

    for neighbor in csp.peers[var]:
        if neighbor not in assignment and value in csp.values[neighbor]:
            if len(csp.values[neighbor]) == 1:
                return "False"

            remaining = csp.values[neighbor] = csp.values[neighbor].replace(value, "")

            if len(remaining) == 1:
                flag = inference(assignment, inferences, csp, neighbor, remaining)
                if flag == "False":
                    return "False"

    return inferences


def is_complete(assignment):
    """
    Judge if the assignment is complete.
    """
    return set(assignment.keys()) == set(grid_names)


def select_unassigned_variables(assignment, csp):
    unassigned_variables = dict(
        (squares, len(csp.values[squares])) for squares in csp.values if squares not in assignment.keys()
    )
    mrv = min(unassigned_variables, key=unassigned_variables.get)
    return mrv


def is_consistent_back_track(var, value, assignment, csp):
    for neighbor in csp.peers[var]:
        if neighbor in assignment.keys() and assignment[neighbor] == value:
            return False
    return True


if __name__ == "__main__":
    render = False
    lines = read_file_to_lines("./data/test.txt")
    solved_num = 0
    solved_algs = []
    for line in lines:
        csp = CSP(grid=line)
        solved = ac_3(csp)
        if csp.is_end() and solved:
            if render:
                print("***************************************")
                print("***************************************")
                print("***************************************")
                print("Before solving: ")
                display_line(line)
                print("After solving use ac-3: ")
                display(csp.values)
            solved_num = solved_num + 1
            solved_algs.append("AC-3")
        else:
            solved = back_track_search(csp)
            if solved != "False":
                if render:
                    print("Before solving: ")
                    display_line(line)
                    print("After solving use back track: ")
                    display(solved)
                solved_algs.append("BACK TRACK")
            else:
                solved_algs.append("NONE")
    print("Number of problems solved is: ", solved_num)
    index = 0
    for alg in solved_algs:
        if alg != "NONE":
            print(f"line {index + 1} is solved by {alg}.")
        else:
            print(f"line {index + 1} not solved.")
        index += 1
