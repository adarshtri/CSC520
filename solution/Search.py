from abc import abstractmethod
import queue
import heapq
import abc
import sys
import time
sys.setrecursionlimit(10000000)

start_time = time.time()


class FileStateInitializer(object):

    """
    Class: Reads a .md file and parses the files to convert into a relevant state configuration.

    __state : Dictionary holding key as current config and value as expected config.
    __filepath: Path of .md file holding state configuration.

    """

    def __init__(self, filepath):

        """
        @:param
        :param filepath: filepath of .md file
        """

        self.__filepath = filepath
        self.__state = []
        self.__goal_test = []
        self.__readfile()

    def __readfile(self):

        try:

            with open(self.__filepath) as fp:
                line = fp.readline()

                while line:

                    line = line.strip()
                    if line == "<Marble>" or line == "</Marble>" or line == "":
                        pass
                    else:

                        # code for each tile parsing

                        line = line[5:]
                        line = line[:-1]
                        tile = line.split(",")

                        cur = (tile[1][2:]+","+tile[2][:-1]).strip()
                        fin = (tile[3]+","+tile[4]).strip()

                        fin = fin[6:]
                        fin = fin[:-1]

                        self.__goal_test.append([int(fin.split(",")[0].strip()), int(fin.split(",")[1].strip())])
                        self.__state.append([int(cur.split(",")[0].strip()), int(cur.split(",")[1].strip())])

                    line = fp.readline()
        except FileNotFoundError:
            raise FileNotFoundError(self.__filepath)

    def get_init_state(self):
        return self.__state

    def get_goal_state(self):
        return self.__goal_test


class Heuristics(metaclass=abc.ABCMeta):

    @staticmethod
    def get_ring_from_state(state):

        """
        :param state:
        :return: list of rings to which the state belongs to.

        eq: equator --> return value 1
        lt1: 0-180 longitude --> return value 2
        lt2: 90-270 longitude --> return value 3
        """

        ring_coordinate_mapping = {
            "eq": [[90, 0], [90, 30], [90, 60], [90, 90], [90, 120], [90, 150], [90, 180], [90, 210], [90, 240], [90, 270], [90, 300], [90, 330]],
            "lt1": [[0, 0], [30, 0], [60, 0], [90, 0], [120, 0], [150, 0],[180, 180], [150, 180], [120, 180],[90, 180],[60, 180], [30, 180]],
            "lt2": [[0, 0], [30, 90], [60, 90], [90, 90], [120, 90], [150, 90], [180, 180], [150, 270], [120, 270], [90, 270], [60, 270], [30, 270]]
        }

        rings = []

        if state in ring_coordinate_mapping["eq"]:
            rings.append(1)

        if state in ring_coordinate_mapping["lt1"]:
            rings.append(2)

        if state in ring_coordinate_mapping["lt2"]:
            rings.append(3)

        return rings

    @staticmethod
    def get_heuristics_on_state(state, goal_state):

        point_to_point_dist_map = {
            (180, 180): {
                (0, 0): 6,
                (180, 180): 0,
                (90, 0): 3,
                (90, 180): 3,
                (90, 90): 3,
                (90, 270): 3
            },
            (150, 270): {
                (0, 0): 5,
                (180, 180): 1,
                (90, 0): 4,
                (90, 180): 4,
                (90, 90): 4,
                (90, 270): 2
            },
            (120, 270): {
                (0, 0): 4,
                (180, 180): 2,
                (90, 0): 4,
                (90, 180): 4,
                (90, 90): 5,
                (90, 270): 1
            },
            (90, 270): {
                (0, 0): 3,
                (180, 180): 3,
                (90, 0): 3,
                (90, 180): 3,
                (90, 90): 6,
                (90, 270): 0
            },
            (60, 270): {
                (0, 0): 2,
                (180, 180): 4,
                (90, 0): 4,
                (90, 180): 4,
                (90, 90): 5,
                (90, 270): 1
            },
            (30, 270): {
                (0, 0): 1,
                (180, 180): 5,
                (90, 0): 4,
                (90, 180): 4,
                (90, 90): 4,
                (90, 270): 2
            },
            (0, 0): {
                (0, 0): 0,
                (180, 180): 6,
                (90, 0): 3,
                (90, 180): 3,
                (90, 90): 3,
                (90, 270): 3
            },
            (30, 90): {
                (0, 0): 1,
                (180, 180): 5,
                (90, 0): 4,
                (90, 180): 4,
                (90, 90): 2,
                (90, 270): 4
            },
            (60, 90): {
                (0, 0): 2,
                (180, 180): 4,
                (90, 0): 4,
                (90, 180): 4,
                (90, 90): 1,
                (90, 270): 5
            },
            (90, 90): {
                (0, 0): 3,
                (180, 180): 3,
                (90, 0): 3,
                (90, 180): 3,
                (90, 90): 0,
                (90, 270): 6
            },
            (120, 90): {
                (0, 0): 4,
                (180, 180): 2,
                (90, 0): 4,
                (90, 180): 4,
                (90, 90): 1,
                (90, 270): 5
            },
            (150, 90): {
                (0, 0): 5,
                (180, 180): 1,
                (90, 0): 4,
                (90, 180): 4,
                (90, 90): 2,
                (90, 270): 4
            },
            (150, 180): {
                (0, 0): 5,
                (180, 180): 1,
                (90, 0): 4,
                (90, 180): 2,
                (90, 90): 4,
                (90, 270): 4
            },
            (120, 180): {
                (0, 0): 4,
                (180, 180): 2,
                (90, 0): 5,
                (90, 180): 1,
                (90, 90): 4,
                (90, 270): 4
            },
            (90, 180): {
                (0, 0): 3,
                (180, 180): 3,
                (90, 0): 6,
                (90, 180): 0,
                (90, 90): 3,
                (90, 270): 3
            },
            (60, 180): {
                (0, 0): 2,
                (180, 180): 4,
                (90, 0): 5,
                (90, 180): 1,
                (90, 90): 4,
                (90, 270): 4
            },
            (30, 180): {
                (0, 0): 1,
                (180, 180): 5,
                (90, 0): 4,
                (90, 180): 2,
                (90, 90): 4,
                (90, 270): 4
            },
            (30, 0): {
                (0, 0): 1,
                (180, 180): 5,
                (90, 0): 2,
                (90, 180): 4,
                (90, 90): 4,
                (90, 270): 4
            },
            (60, 0): {
                (0, 0): 2,
                (180, 180): 4,
                (90, 0): 1,
                (90, 180): 5,
                (90, 90): 4,
                (90, 270): 4
            },
            (90, 0): {
                (0, 0): 3,
                (180, 180): 3,
                (90, 0): 0,
                (90, 180): 6,
                (90, 90): 3,
                (90, 270): 3
            },
            (120, 0): {
                (0, 0): 4,
                (180, 180): 2,
                (90, 0): 1,
                (90, 180): 5,
                (90, 90): 4,
                (90, 270): 4
            },
            (150, 0): {
                (0, 0): 5,
                (180, 180): 1,
                (90, 0): 2,
                (90, 180): 4,
                (90, 90): 4,
                (90, 270): 4
            },
            (90, 240): {
                (0, 0): 4,
                (180, 180): 4,
                (90, 0): 4,
                (90, 180): 2,
                (90, 90): 5,
                (90, 270): 1
            },
            (90, 210): {
                (0, 0): 4,
                (180, 180): 4,
                (90, 0): 5,
                (90, 180): 1,
                (90, 90): 4,
                (90, 270): 2
            },
            (90, 150): {
                (0, 0): 4,
                (180, 180): 4,
                (90, 0): 5,
                (90, 180): 1,
                (90, 90): 2,
                (90, 270): 4
            },
            (90, 120): {
                (0, 0): 4,
                (180, 180): 4,
                (90, 0): 4,
                (90, 180): 2,
                (90, 90): 1,
                (90, 270): 5
            },
            (90, 60): {
                (0, 0): 4,
                (180, 180): 4,
                (90, 0): 2,
                (90, 180): 4,
                (90, 90): 1,
                (90, 270): 5
            },
            (90, 30): {
                (0, 0): 4,
                (180, 180): 4,
                (90, 0): 1,
                (90, 180): 5,
                (90, 90): 2,
                (90, 270): 4
            },
            (90, 330): {
                (0, 0): 4,
                (180, 180): 4,
                (90, 0): 1,
                (90, 180): 5,
                (90, 90): 4,
                (90, 270): 2
            },
            (90, 300): {
                (0, 0): 4,
                (180, 180): 4,
                (90, 0): 2,
                (90, 180): 4,
                (90, 90): 5,
                (90, 270): 1
            }
        }

        x_00 = goal_state.index([0, 0])
        x_180180 = goal_state.index([180, 180])
        x_9090 = goal_state.index([90, 90])
        x_90270 = goal_state.index([90, 270])
        x_900 = goal_state.index(([90, 0]))
        x_90180 = goal_state.index([90, 180])

        x_cur_00 = tuple(state[x_00])
        x_cur_180180 = tuple(state[x_180180])
        x_cur_9090 = tuple(state[x_9090])
        x_cur_90270 = tuple(state[x_90270])
        x_cur_900 = tuple(state[x_900])
        x_cur_90180 = tuple(state[x_90180])

        sum = point_to_point_dist_map[x_cur_00][(0, 0)] + point_to_point_dist_map[x_cur_180180][(180, 180)] + point_to_point_dist_map[x_cur_9090][(90, 90)] + point_to_point_dist_map[x_cur_90270][(90, 270)] + point_to_point_dist_map[x_cur_900][(90, 0)] + point_to_point_dist_map[x_cur_90180][(90, 180)]
        return sum/6


class Search(metaclass=abc.ABCMeta):

    """
    actions: mapping from action to degree conversion.
    1: Increment equator tiles by 30
    2: Decrement equator tiles by 30
    3. Increment longitude 0-180 tiles by 30
    4: Decrement longitude 0-180 tiles by 30
    5: Increment longitude 90-270 tiles by 30
    6: Decrement longitude 90-270 tiles by 30
    """

    actions = {
        1: +30,
        2: -30
    }

    eq = 1
    lt0180 = 2
    lt90270 = 3

    valid_states = [
        [180,180], [150,270], [120,270], [90,270], [60,270], [30,270],[0,0],[30,90],[60,90],[90,90],[120,90],[150,90],
        [150,180],[120,180],[90,180],[60,180],[30,180],[30,0],[60,0],[90,0],[120,0],[150,0],
        [90,240],[90,210],[90,150],[90,120],[90,60],[90,30],[90,330], [90,300]
    ]

    def __init__(self, filepath):
        self.__filepath = filepath
        self._state = FileStateInitializer(filepath=filepath).get_init_state()
        self._goal_test = FileStateInitializer(filepath=filepath).get_goal_state()
        self._explored_states = None
        self._frontier = None

    @staticmethod
    def get_rings_of_lat_long(lat, long):
        rings = []

        if lat == 90:
            rings.append(Search.eq)

        if long == 0 or long == 180:
            rings.append(Search.lt0180)

        if long == 90 or long == 270:
            rings.append(Search.lt90270)

        return rings

    @staticmethod
    def rotate_around_equator(state_i, degree_movement):

        state = []
        for s in state_i:
            state.append(s[:])

        for state_elem in state:
            if state_elem[0] == 90:
                state_elem[1] = (state_elem[1] + degree_movement) % 360

        return state

    @staticmethod
    def rotate_around_longitude_0_180(state_i, degree_movement):

        state = []
        for s in state_i:
            state.append(s[:])

        for state_ele in state:

            if state_ele[1] in [0,180]:

                if state_ele[0] == 0 and state_ele[1] == 0 and degree_movement < 0:
                    state_ele[1] = 180
                    state_ele[0] = 30

                elif state_ele[0] == 150 and state_ele[1] == 0 and degree_movement > 0:
                    state_ele[1] = 180
                    state_ele[0] = 180

                elif state_ele[0] == 180 and state_ele[1] == 180 and degree_movement < 0:
                    state_ele[1] = 0
                    state_ele[0] = 150

                elif state_ele[0] == 30 and state_ele[1] == 180 and degree_movement > 0:
                    state_ele[1] = 0
                    state_ele[0] = 0

                else:

                    if state_ele[1] == 0:
                        state_ele[0] += degree_movement
                    else:
                        state_ele[0] -= degree_movement
        return state

    @staticmethod
    def rotate_around_longitude_90_270(state_i, degree_movement):

        state = []
        for s in state_i:
            state.append(s[:])

        for state_ele in state:
            if state_ele[1] in [90, 270, 180, 0]:
                if state_ele[0] == 0 and state_ele[0] == 0:
                    if degree_movement > 0:
                        state_ele[0] = 30
                        state_ele[1] = 90
                    else:
                        state_ele[0] = 30
                        state_ele[1] = 270

                elif state_ele[0] == 180 and state_ele[1] == 180:
                    if degree_movement > 0:
                        state_ele[0] = 150
                        state_ele[1] = 270
                    else:
                        state_ele[0] = 150
                        state_ele[1] = 90

                elif state_ele[0] == 150 and state_ele[1] == 90:

                    if degree_movement > 0:
                        state_ele[0] = 180
                        state_ele[1] = 180
                    else:
                        state_ele[0] = 120
                        state_ele[1] = 90

                elif state_ele[0] == 30 and state_ele[1] == 270:

                    if degree_movement > 0:
                        state_ele[0] = 0
                        state_ele[1] = 0

                    else:
                        state_ele[0] = 60
                        state_ele[1] = 270

                elif state_ele[0] == 30 and state_ele[1] == 90:

                    if degree_movement < 0:
                        state_ele[0] = 0
                        state_ele[1] = 0

                    else:
                        state_ele[0] = 60
                        state_ele[1] = 90

                elif state_ele[0] == 150 and state_ele[1] == 270:
                    if degree_movement < 0:
                        state_ele[0] = 180
                        state_ele[1] = 180

                    else:
                        state_ele[0] = 120
                        state_ele[1] = 270

                else:
                    if state_ele[1] == 90:
                        state_ele[0] += degree_movement
                    elif state_ele[1] == 270:
                        state_ele[0] -= degree_movement
        return state

    @abstractmethod
    def search(self):
        pass


class RecursiveBestFirstSearch(Search, Heuristics):

    def __init__(self, filepath):
        Search.__init__(self, filepath=filepath)
        self._frontier = []
        self._closed_state = set()
        self._final_cost = 0
        self._i = 0
        self._j = 1

    def search(self):
        result = self.rbfs(self._state, 999999, 0, Heuristics.get_heuristics_on_state(self._state, self._goal_test),[])
        if result[0]:
            print("Found")
            print("%s%d" % ("Total states explored:", len(self._closed_state)))
            print("Final path:", str(result[2]))
        else:
            print("Not found")
        return self._final_cost

    def rbfs(self, state, flim, cost, f, statepath):

        if state == self._goal_test:
            if self._final_cost < cost:
                self._final_cost = cost
            return True, cost, statepath

        self._i += 1

        if self._i % 5000 == 0 and (time.time() - start_time) >= 100 * self._j:
            print("Logging RBFS for file " + sys.argv[2] + " after " + str(time.time() - start_time) + " seconds.",
                  flush=True)
            print("%s%d" % ("Total states explored:", len(self._closed_state)), flush=True)
            print("Current path length: %d" % cost, flush=True)
            print("-----------------------------------------------", flush=True)

            self._j += 1

        self._closed_state.add(str(state))

        successors = []

        state1 = Search.rotate_around_equator(state, 30)
        state2 = Search.rotate_around_equator(state, -30)
        state3 = Search.rotate_around_longitude_0_180(state, 30)
        state4 = Search.rotate_around_longitude_0_180(state, -30)
        state5 = Search.rotate_around_longitude_90_270(state, 30)
        state6 = Search.rotate_around_longitude_90_270(state, -30)

        heuristic1 = Heuristics.get_heuristics_on_state(state1, self._goal_test)
        heuristic2 = Heuristics.get_heuristics_on_state(state2, self._goal_test)
        heuristic3 = Heuristics.get_heuristics_on_state(state3, self._goal_test)
        heuristic4 = Heuristics.get_heuristics_on_state(state4, self._goal_test)
        heuristic5 = Heuristics.get_heuristics_on_state(state5, self._goal_test)
        heuristic6 = Heuristics.get_heuristics_on_state(state6, self._goal_test)

        successors.append([max(f, heuristic1+cost), state1, statepath+["eq_inc"]])
        successors.append([max(f, heuristic2+cost), state2, statepath+["eq_dec"]])
        successors.append([max(f, heuristic3+cost), state3, statepath+["0180_inc"]])
        successors.append([max(f, heuristic4+cost), state4, statepath+["0180_dec"]])
        successors.append([max(f, heuristic5+cost), state5, statepath+["90270_inc"]])
        successors.append([max(f, heuristic6+cost), state6, statepath+["90270_dec"]])

        heapq.heapify(successors)

        while True:

            if successors[0][0] > flim:
                return False, successors[0][0], statepath

            alternative = successors[1]
            result, successors[0][0], sp = self.rbfs(successors[0][1], min(alternative[0], flim), cost+1, successors[0][0], successors[0][2])
            heapq.heapify(successors)

            if result:
                if self._final_cost < cost:
                    self._final_cost = cost
                return True, cost, sp


class AStar(Search, Heuristics):

    def __init__(self, filepath):
        Search.__init__(self, filepath=filepath)
        self._frontier = []
        self._closed_set = set()
        self._max_frontier_length = 0

    def search(self):
        start_score = 0
        heapq.heappush(self._frontier, (1, self._state, 0, []))

        i = 0
        j = 1

        while self._frontier:

            i += 1

            current_state_heap_ele = heapq.heappop(self._frontier)
            current_state = current_state_heap_ele[1]
            tentative_score = current_state_heap_ele[0]
            g_score = current_state_heap_ele[2]
            statepath = current_state_heap_ele[3]

            if i % 5000 == 0 and (time.time()-start_time) >= 100*j:
                print("Logging AStar for file " + sys.argv[2] + " after " + str(time.time()-start_time) + " seconds.", flush=True)
                print("%s%d" % ("Total states explored:", len(self._closed_set)), flush=True)
                print("Maximum frontier length:", str(self._max_frontier_length))
                print("Current path length: %d" % g_score, flush=True)
                print("-----------------------------------------------", flush=True)

                j += 1

            if current_state == self._goal_test:
                print("Found", flush=True)
                print("%s%d" % ("Total states explored:", len(self._closed_set)), flush=True)
                print("Final path length:%d" % g_score, flush=True)
                print("Maximum frontier length:", str(self._max_frontier_length))
                print("Final path: " + str(statepath), flush=True)
                print("--------------------------------------------------", flush=True)
                break

            if str(current_state) in self._closed_set:
                continue

            else:

                self._closed_set.add(str(current_state))

                state1 = Search.rotate_around_equator(current_state, 30)
                state2 = Search.rotate_around_equator(current_state, -30)
                state3 = Search.rotate_around_longitude_0_180(current_state, 30)
                state4 = Search.rotate_around_longitude_0_180(current_state, -30)
                state5 = Search.rotate_around_longitude_90_270(current_state, 30)
                state6 = Search.rotate_around_longitude_90_270(current_state, -30)

                if str(state1) not in self._closed_set:
                    heapq.heappush(self._frontier,
                                   (g_score+self.get_heuristics_on_state(state1, self._goal_test), state1, g_score+1,
                                    statepath+["eq_inc"]))

                if str(state2) not in self._closed_set:
                    heapq.heappush(self._frontier,
                                   (g_score+self.get_heuristics_on_state(state2, self._goal_test), state2, g_score+1,
                                    statepath+["eq_dec"]))

                if str(state3) not in self._closed_set:
                    heapq.heappush(self._frontier,
                                   (g_score+self.get_heuristics_on_state(state3, self._goal_test), state3, g_score+1,
                                    statepath+["0180_inc"]))

                if str(state4) not in self._closed_set:
                    heapq.heappush(self._frontier,
                                   (g_score+self.get_heuristics_on_state(state4, self._goal_test), state4, g_score+1,
                                    statepath+["0180_dec"]))

                if str(state5) not in self._closed_set:
                    heapq.heappush(self._frontier,
                                   (g_score+self.get_heuristics_on_state(state5, self._goal_test), state5, g_score+1,
                                    statepath+["90270_inc"]))

                if str(state6) not in self._closed_set:
                    heapq.heappush(self._frontier,
                                   (g_score+self.get_heuristics_on_state(state6, self._goal_test), state6, g_score+1,
                                    statepath+["90270_dec"]))

                if len(self._frontier) > self._max_frontier_length:
                    self._max_frontier_length = len(self._frontier)


class BreadthFirstSearch(Search):

    def __init__(self, filepath):
        Search.__init__(self, filepath=filepath)
        self._frontier = queue.Queue(maxsize=0)
        self._explored_states = set()
        self._max_frontier_length = 0

    def search(self):

        self._frontier.put((self._state, 0, []))

        if self._state == self._goal_test:
            return "Found"

        i = 0
        j = 1

        while not self._frontier.empty():

            i += 1

            curstateele = self._frontier.get()

            curstate = curstateele[0]
            curcost = curstateele[1]
            curstatepath = curstateele[2]

            if i % 1000 == 0 and (time.time()-start_time) >= 100*j:
                print("Logging BFS for file " + sys.argv[2] + " after " + str(time.time()-start_time) + " seconds.", flush=True)
                print("%s%d" % ("Total states explored:", len(self._explored_states)), flush=True)
                print("Maximum frontier length:", str(self._max_frontier_length))
                print("Current path length: %d" % curcost, flush=True)
                print("-----------------------------------------------", flush=True)

                j += 1

            if curstate == self._goal_test:
                print("Found", flush=True)
                print("%s%d" % ("Total states explored:", len(self._explored_states)), flush=True)
                print("Maximum frontier length:", str(self._max_frontier_length))
                print("Final path length:%d" % curcost, flush=True)
                print("Final path: " + str(curstatepath), flush=True)
                break

            self._explored_states.add(str(curstate))

            state1 = Search.rotate_around_equator(curstate, 30)
            state2 = Search.rotate_around_equator(curstate, -30)
            state3 = Search.rotate_around_longitude_0_180(curstate, 30)
            state4 = Search.rotate_around_longitude_0_180(curstate, -30)
            state5 = Search.rotate_around_longitude_90_270(curstate, 30)
            state6 = Search.rotate_around_longitude_90_270(curstate, -30)

            if str(state1) not in self._explored_states:
                self._frontier.put((state1, curcost+1, curstatepath+["eq_inc"]))

            if str(state2) not in self._explored_states:
                self._frontier.put((state2, curcost+1, curstatepath+["eq_dec"]))

            if str(state3) not in self._explored_states:
                self._frontier.put((state3, curcost+1, curstatepath+["0180_inc"]))

            if str(state4) not in self._explored_states:
                self._frontier.put((state4, curcost+1, curstatepath+["0180_dec"]))

            if str(state5) not in self._explored_states:
                self._frontier.put((state5, curcost+1, curstatepath+["90270_inc"]))

            if str(state6) not in self._explored_states:
                self._frontier.put((state6, curcost+1, curstatepath+["90270_dec"]))

            if self._frontier.qsize() > self._max_frontier_length:
                self._max_frontier_length = self._frontier.qsize()

        else:
            print("Not found")


algo = sys.argv[1]
file = sys.argv[2]

obj = None

if algo == "BFS":
    obj = BreadthFirstSearch(filepath=file)
    #sys.stdout = open(file + ".bfs.log", 'w')
elif algo == "AStar":
    obj = AStar(filepath=file)
    #sys.stdout = open(file + ".astar.log", 'w')
elif algo == "RBFS":
    obj = RecursiveBestFirstSearch(filepath=file)
    #sys.stdout = open(file + ".rbfs.log", 'w')
else:
    print("Invalid algorithm.")
    exit(0)
obj.search()
