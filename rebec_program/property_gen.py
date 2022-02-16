import random
from utils.utils import weighted_random_choices, flatten_list, pairwise, weighted_random_choice, \
    remove_duplicates_array, tuple_to_string
from utils.name_gen import name_gen
from termcolor import colored
import itertools


class property_gen():
    def __init__(self, msgservers_graph, configuration):
        self.msgservers_graph = msgservers_graph
        self.causality_count = configuration.causality_count
        self.deadlock_count = configuration.deadlock_count
        self.deadlock_length = configuration.deadlock_length
        self.non_causality_count = configuration.non_causality_count
        self.property_length = configuration.property_length
        self.strictly = configuration.strictly

        self.causality_msgservers = list()
        self.non_causality_msgservers = list()
        self.causality_set = list()
        self.non_causality_set = list()
        self.deadlock_property = list()
        self.deadlock_property_msgservers = list()
        self.repetitive_deadlock = list()

    def set_deadlock_property_msgservers(self, deadlock_property_msgservers):
        self.deadlock_property_msgservers = deadlock_property_msgservers

    def set_repetitive_deadlock(self, repetitive_deadlock):
        self.repetitive_deadlock = repetitive_deadlock

    def get_deadlock_property(self):
        return self.deadlock_property

    def get_property_set(self):
        return self.choose_property_set()

    def get_deadlock_property_msgservers(self):
        return self.deadlock_property_msgservers

    def fix_format(self, arr):
        return [self.convert_edge_to_property_seq(edge) for edge in arr]

    def choose_property_set(self):

        self.causality_msgservers = self.choose_causality_property_set()
        causality_set = [self.fix_format(p) for p in self.causality_msgservers]
        causality_set = remove_duplicates_array(causality_set)
        # print('causality_set', causality_set)

        self.non_causality_msgservers = self.choose_non_causality_property_set()

        self.generate_deadlock(self.non_causality_msgservers)
        self.deadlock_property_msgservers = self.deadlock_property.copy()
        self.repetitive_deadlock = [self.fix_format(p) for p in self.repetitive_deadlock]
        self.deadlock_property = [self.fix_format(p) for p in self.deadlock_property]
        # print("ccccccccccccc ",self.deadlock_property_msgservers)
        # remove_duplicates_array(self.deadlock_property)

        non_causality_set = [self.fix_format(p) for p in self.non_causality_msgservers]
        non_causality_set = remove_duplicates_array(non_causality_set)
        # print('non_causality_set', non_causality_set)

        self.causality_set = causality_set
        self.non_causality_set = non_causality_set

        return causality_set + non_causality_set

    def generate_deadlock(self, non_causality_set):
        if self.strictly:
            self.generate_deadlock_strictly(non_causality_set)
        else:
            number = 0
            while number != 30:
                self.generate_deadlock_not_strictly(non_causality_set)
                if self.two_message_in_row(non_causality_set):
                    print("Generate wrong deadlock make repetitive path. will try again ")

                    number += 1
                else:
                    break

            if number == 30:
                print("Generate wrong deadlock make repetitive path . ")
                exit(1)

    def two_message_in_row(self, non_causality_path):
        for path in non_causality_path:
            for msg in range(len(path) - 1):
                if path[msg][0][0] == path[msg + 1][0][0] and path[msg][1] == path[msg + 1][1]:
                    print("Repetitive path", path)
                    return True
        return False

    def generate_deadlock_with_same_property(self, deadlock_property_strictly):
        selected = random.choice(deadlock_property_strictly)
        if self.deadlock_length == 2:
            return selected
        # print("ppppp", selected)
        deadlock_path = self.generate_non_causal_deadlcok_path(self.deadlock_length, selected.copy())
        return deadlock_path


    def is_senders_different(self, path1, path2):
        senders = []
        for msg in path1:
            senders.append(msg[0][0])
        if path2[0][0] in senders:
            return False
        return True

    def is_start_with_it(self, starter, paths):
        for path in paths:
            if starter[0] == path[0] and starter[1] == path[1]:
                return True
        return False

    def generate_non_causal_deadlcok_path(self, path_length, initial_path):
        new_path = initial_path
        two = self.msgservers_graph.all_paths_with_length(2)
        three = self.msgservers_graph.all_paths_with_length(3)
        non_causal_prop = []
        for prp in two:
            if not self.is_start_with_it(prp, three):
                non_causal_prop.append(prp)

        paths = self.remove_duplicates(
            self.get_weighted_paths_helper_shorter(
                non_causal_prop))
        # print("eeeeeeeeeee", new_path)
        # print("eeeeeeeeeee", paths)
        random.shuffle(paths)
        while len(paths) != 0:
            path = paths.pop()
            for edge in path[0]:
                if edge in new_path or not self.is_senders_different(new_path, edge):
                    continue
                else:
                    new_path.append(edge)
                    break
            if len(new_path) == path_length:
                return new_path
        return None

    def generate_deadlock_not_strictly(self, non_causality_set):
        self.repetitive_deadlock = []
        self.deadlock_property = []
        deadlock_property_strictly = []
        deadlock_paths = []
        last_two = 2
        path_needed = self.deadlock_count * self.deadlock_length
        extra_path = path_needed - self.non_causality_count
        i = 0

        while i < len(non_causality_set) and path_needed != 0:
            if self.deadlock_count == 0:
                return

            try_number = 0
            while try_number != 10:
                if extra_path > 0 and len(deadlock_property_strictly) > 0:
                    deadlock_path = self.generate_deadlock_with_same_property(deadlock_property_strictly)
                    if deadlock_path is None or self.is_path_generate_before(deadlock_path.copy(), deadlock_paths):
                        try_number += 1
                        continue
                    extra_path -= 1

                else:
                    # deadlock_path = self.generate_non_causal_path(self.deadlock_length)
                    deadlock_path = self.generate_non_causal_deadlcok_path(self.deadlock_length, [])
                    if deadlock_path is None or not self.is_all_different_sender(deadlock_path) or\
                            self.is_path_generate_before(deadlock_path.copy(), deadlock_paths):
                        try_number += 1
                        continue

                break

            if try_number == 10:
                print(
                    colored("Can't find non causality path to generate  deadlock!", 'yellow',
                            attrs=['bold']))
                exit(1)

            # deadlock_paths.append(deadlock_path)
            # print("deadlock_path", deadlock_path)
            deadlock_prop = self.extract_not_strictly_deadlock_property(deadlock_path)
            # print("deadlock_prop", deadlock_prop)
            self.make_circle_for_show(deadlock_path)
            counter = 0
            while i < len(non_causality_set) and counter != self.deadlock_length:

                if deadlock_prop[counter] in deadlock_property_strictly:
                    self.repetitive_deadlock.append(deadlock_prop[counter])
                    deadlock_property_strictly.append(deadlock_prop[counter])
                    counter += 1
                    path_needed -= 1
                    continue
                non_causality_set[i][-last_two:] = deadlock_prop[counter]
                deadlock_property_strictly.append(deadlock_prop[counter])
                i += 1
                counter += 1
                path_needed -= 1

        # print("deadlock_property_strictly", deadlock_property_strictly)
        print("repetitive_deadlock", self.repetitive_deadlock)
        if path_needed > 0:
            print(
                colored("Could not to generate all deadlock!", 'yellow',
                        attrs=['bold']))

    def enhance_deadlock_length_not_strictly(self, paths_without_deadlock, paths_with_deadlock, deadlock_msgservers, repetitive_deadlock):
        print("deadlock_msgservers", deadlock_msgservers)
        if len(paths_without_deadlock) < len(deadlock_msgservers):
            print("There is n0t enough non casual to enhance length ")
            exit(1)

        deadlock_paths = []
        for i in range(len(deadlock_msgservers)):
            for path_with_deadlock in paths_with_deadlock:
                if deadlock_msgservers[i][-2:] == path_with_deadlock[-2:]:
                    deadlock_msgservers[i].pop()
                    # print("pppp", deadlock_msgservers[i])
                    deadlock_path = self.generate_non_causal_deadlcok_path(self.deadlock_length, deadlock_msgservers[i])
                    if deadlock_path is None or not self.is_all_different_sender(deadlock_path) or\
                            self.is_path_generate_before(deadlock_path.copy(), deadlock_paths):

                        print("Can't enhance length")
                        exit(1)
                    deadlock_prop = self.extract_not_strictly_deadlock_property(deadlock_path)
                    self.make_circle_for_show(deadlock_path)

                    path_with_deadlock[-2:] = deadlock_prop.pop()
                    path = paths_without_deadlock.pop()
                    path[-2:] = deadlock_prop.pop()
                    paths_with_deadlock.append(path)
                    break

        print("paths_with_deadlock", paths_with_deadlock)
        print("deadlock_paths", deadlock_paths)
        self.deadlock_property_msgservers = self.deadlock_property
        self.deadlock_property = [self.fix_format(p) for p in self.deadlock_property_msgservers]
        self.non_causality_msgservers = paths_without_deadlock + paths_with_deadlock
        self.non_causality_set = [self.fix_format(p) for p in self.non_causality_msgservers]
        self.repetitive_deadlock = self.repetitive_deadlock + repetitive_deadlock
        #
        # self.deadlock_property_msgservers = deadlock_msgservers
        # self.deadlock_property = [self.fix_format(p) for p in self.deadlock_property_msgservers]
        # self.non_causality_msgservers = paths_without_deadlock + paths_with_deadlock
        # self.non_causality_set = [self.fix_format(p) for p in self.non_causality_msgservers]

    def is_path_generate_before(self, path, paths):
        modify_path = []
        for i in path:
            modify_path.append((i[0][0], i[1]))
        # print("paths",paths)
        for i in range(self.deadlock_length):
            modify_path.append(modify_path.pop(0))
            for p in paths:
                if modify_path == p:
                    return True

        paths.append(modify_path)
        return False

    def enhance_deadlock_count_not_strictly(self, paths_without_deadlock, paths_with_deadlock, deadlock_msgservers, repetitive_deadlock):
        last_two = 2
        enhanced = False
        deadlock_paths = []

        for deadlock in deadlock_msgservers:
            deadlock.pop()

            self.is_path_generate_before(deadlock, deadlock_paths)

        deadlock_property_strictly = []

        for deadlock in deadlock_msgservers:
            deadlock_prp = self.extract_not_strictly_deadlock_property(deadlock)
            deadlock_prp.pop()
            for p in deadlock_prp:
                deadlock_property_strictly.append(p)

        i = 0
        while i < len(paths_without_deadlock) and not enhanced:

            try_number = 0
            while try_number != 10:
                deadlock_path = self.generate_non_causal_deadlcok_path(self.deadlock_length, [])
                if deadlock_path is None or not self.is_all_different_sender(deadlock_path) or\
                        self.is_path_generate_before(deadlock_path.copy(), deadlock_paths):
                    try_number += 1
                    continue

                break

            if try_number == 10:
                print(
                    colored("Can't find non causality path to generate  deadlock!", 'yellow',
                            attrs=['bold']))
                exit(1)

            deadlock_prop = self.extract_not_strictly_deadlock_property(deadlock_path)

            self.make_circle_for_show(deadlock_path)
            counter = 0
            while i < len(paths_without_deadlock) and counter != self.deadlock_length:
                if deadlock_prop[counter] in deadlock_property_strictly:
                    self.repetitive_deadlock.append(deadlock_prop[counter])
                    deadlock_property_strictly.append(deadlock_prop[counter])
                    counter += 1

                    continue

                paths_without_deadlock[i][-last_two:] = deadlock_prop[counter]
                deadlock_property_strictly.append(deadlock_prop[counter])
                i += 1
                counter += 1
            if counter == self.deadlock_length:
                enhanced = True

        # print("deadlock_property_strictly", deadlock_property_strictly)
        print("repetitive_deadlock", self.repetitive_deadlock)
        if not enhanced:
            print(
                colored("Could not to generate all deadlock!", 'yellow',
                        attrs=['bold']))
            exit(1)
        else:
            for dead in deadlock_msgservers:
                self.make_circle_for_show(dead)
            self.deadlock_property_msgservers = self.deadlock_property
            self.deadlock_property = [self.fix_format(p) for p in self.deadlock_property_msgservers]
            self.non_causality_msgservers = paths_without_deadlock + paths_with_deadlock
            self.non_causality_set = [self.fix_format(p) for p in self.non_causality_msgservers]
            self.repetitive_deadlock = self.repetitive_deadlock + repetitive_deadlock



    def seperate_deadlock_non_casuality(self, non_casuality_msgservers, deadlock_msgservers):
        paths_with_deadlock = list()
        if self.strictly:
            for non_casual in non_casuality_msgservers:
                for deadlock in deadlock_msgservers:
                    if non_casual[-self.deadlock_length:] == deadlock:
                        paths_with_deadlock.append(non_casual)

        else:
            deadlock_prps = []

            for deadlock in deadlock_msgservers:
                deadlock_prp = self.extract_not_strictly_deadlock_property(deadlock)
                deadlock_prp.pop()
                for p in deadlock_prp:
                    deadlock_prps.append(p)

            for non_casual in non_casuality_msgservers:
                for deadlock in deadlock_prps:
                    if non_casual[-2:] == deadlock:
                        paths_with_deadlock.append(non_casual)

        paths_without_deadlock = [x for x in non_casuality_msgservers if x not in paths_with_deadlock]
        print("non_casuality_msgservers", non_casuality_msgservers)
        print("paths_without_deadlock", paths_without_deadlock)
        return paths_without_deadlock, paths_with_deadlock

    def enhance_deadlock_length_property_set(self, non_casuality_msgservers, deadlock_msgservers, repetitive_deadlock):
        paths_without_deadlock, paths_with_deadlock = self.seperate_deadlock_non_casuality(non_casuality_msgservers,deadlock_msgservers)

        if self.strictly:
            self.enhance_deadlock_length_strictly(paths_without_deadlock, paths_with_deadlock, deadlock_msgservers)
            # set casul
        else:

            self.enhance_deadlock_length_not_strictly(paths_without_deadlock, paths_with_deadlock, deadlock_msgservers, repetitive_deadlock)

        return self.non_causality_set

    def enhance_deadlock_count_property_set(self, non_casuality_msgservers, deadlock_msgservers, repetitive_deadlock):
        paths_without_deadlock, paths_with_deadlock = self.seperate_deadlock_non_casuality(non_casuality_msgservers,deadlock_msgservers)

        if self.strictly:
            self.enhance_deadlock_count_strictly(paths_without_deadlock, paths_with_deadlock, deadlock_msgservers)
            # set casul
        else:

            self.enhance_deadlock_count_not_strictly(paths_without_deadlock, paths_with_deadlock, deadlock_msgservers, repetitive_deadlock)

        return self.non_causality_set

    def enhance_deadlock_count_strictly(self, paths_without_deadlock, paths_with_deadlock, deadlock_msgservers):
        if 2 > len(paths_without_deadlock):
            print(
                colored("There is not enough non causality path for generate all deadlock!", 'yellow', attrs=['bold']))
        enhanced = False
        for i in range(1, len(paths_without_deadlock), 2):
            if enhanced:
                return
            if self.two_sender_message_in_row(paths_without_deadlock[i - 1]):
                continue

            deadlock_path = self.generate_non_causal_deadlcok_path(self.deadlock_length, [])
            if deadlock_path is None:
                continue
            paths_without_deadlock[i - 1][-self.deadlock_length:] = deadlock_path
            paths_without_deadlock[i][-self.deadlock_length:] = deadlock_path[::-1]
            self.deadlock_count -= 1
            deadlock_msgservers.append(deadlock_path)
            deadlock_msgservers.append(deadlock_path[::-1])
            # print("deadlock_property :",self.deadlock_property)
            enhanced = True
            # print(non_causality_set[i-1])
            # print(non_causality_set[i])

        if not enhanced:
            print(colored("Could not enhance deadlock. ", 'magenta', attrs=['bold']))
        else:
            self.deadlock_property_msgservers = deadlock_msgservers
            self.deadlock_property = [self.fix_format(p) for p in self.deadlock_property_msgservers]
            self.non_causality_msgservers = paths_without_deadlock + paths_with_deadlock
            self.non_causality_set = [self.fix_format(p) for p in self.non_causality_msgservers]

    def make_circle_for_show(self, deadlock_path):
        deadlock_path.append(deadlock_path[0])
        self.deadlock_property.append(deadlock_path)

    def extract_not_strictly_deadlock_property(self, deadlock_path):
        deadlock_prop = []
        for i in range(1, len(deadlock_path)):
            deadlock_prop.append([deadlock_path[i - 1], deadlock_path[i]])
            if i == len(deadlock_path) - 1:
                deadlock_prop.append([deadlock_path[i], deadlock_path[0]])
        return deadlock_prop

    def is_all_different_sender(self, path):
        sender = []
        for p in path:
            if p[0][0] in sender:
                return False
            else:
                sender.append(p[0][0])
        return True

    def generate_deadlock_strictly(self, non_causality_set):
        if self.property_length < self.deadlock_length:
            print(colored("Property length is bigger that deadlock length!!!", 'yellow', attrs=['bold']))
            print("Could not generate all deadlock. ")
            return

        if self.deadlock_count > self.non_causality_count // 2:
            print(
                colored("There is not enough non causality path for generate all deadlock!", 'yellow', attrs=['bold']))

        if len(non_causality_set) <= 1:  # not enough non_causality_set to generate deadlock
            return
        for i in range(1, len(non_causality_set), 2):
            if self.deadlock_count == 0:
                return
            if self.two_sender_message_in_row(non_causality_set[i - 1]):
                continue

            deadlock_path = self.generate_non_causal_deadlcok_path(self.deadlock_length, [])
            if deadlock_path is None:
                continue
            non_causality_set[i - 1][-self.deadlock_length:] = deadlock_path
            non_causality_set[i][-self.deadlock_length:] = deadlock_path[::-1]
            self.deadlock_count -= 1
            self.deadlock_property.append(deadlock_path)
            self.deadlock_property.append(deadlock_path[::-1])
            # print("deadlock_property :",self.deadlock_property)

            # print(non_causality_set[i-1])
            # print(non_causality_set[i])

        if self.deadlock_count != 0:
            print(colored("Could not generate all deadlock. ", 'magenta', attrs=['bold']))

    def two_sender_message_in_row(self, non_causality_path):
        # for msg in range(self.property_length - self.deadlock_length, self.property_length - 1):
        for msg in range(len(non_causality_path) - 1):
            if non_causality_path[msg][0][0] == non_causality_path[msg + 1][0][0]:
                return True
        return False

    def enhance_non_causality_property_set(self, paths):
        non_causal_paths = list()
        wrong_paths_limit = 30
        repeated_paths_count, none_count = 0, 0
        p = paths.pop()
        try:
            while True:
                if len(p) == self.property_length:
                    non_causal_paths.append(p)
                    p = paths.pop()
                    continue
                new_path = self.generate_non_causal_path(self.property_length, path=p)
                if new_path is None:
                    none_count += 1
                    if none_count == wrong_paths_limit:
                        assert False, "Algorithm cannot find any non causal path with length " + str(
                            self.property_length) + ". Maybe graph doesn't have enough edges or it's completely causal."
                    else:
                        continue
                if new_path not in non_causal_paths:
                    non_causal_paths.append(new_path)
                    none_count = 0
                    p = paths.pop()
                else:
                    repeated_paths_count += 1
                if repeated_paths_count == wrong_paths_limit:
                    # sets a maximum limit to repeated paths (when it occurs, it means that the algorithm can't genreate a new path)
                    assert False, "Maximum number of non causal paths is " + str(len(non_causal_paths)) + ", but required is " + str(self.non_causality_count)
        except IndexError:
            self.non_causality_msgservers = non_causal_paths
            print("PATHS NON CAUSAL:", non_causal_paths)
            non_causality_set = remove_duplicates_array(
                [self.fix_format(p) for p in self.choose_non_causality_property_set()])
            print("\nNon causal properties", non_causality_set)
            self.non_causality_set = non_causality_set
            return non_causality_set

    def choose_non_causality_property_set(self):
        non_causal_paths = self.non_causality_msgservers
        wrong_paths_limit = 30
        repeated_paths_count, none_count = 0, 0
        while len(non_causal_paths) < self.non_causality_count:
            new_path = self.generate_non_causal_path(self.property_length)
            if new_path is None:
                none_count += 1
                if none_count == wrong_paths_limit:
                    assert False, "Algorithm cannot find any non causal path with length " + str(
                        self.property_length) + ". Maybe graph doesn't have enough edges or it's completely causal."
                else:
                    continue
            if new_path not in non_causal_paths:
                non_causal_paths.append(new_path)
                none_count = 0
            else:
                repeated_paths_count += 1
            if repeated_paths_count == wrong_paths_limit:  # sets a maximum limit to repeated paths (when it occurs, it means that the algorithm can't genreate a new path)
                assert False, "Maximum number of non causal paths is " + str(
                    len(non_causal_paths)) + ", but required is " + str(self.non_causality_count)

        print("Non causal properties", non_causal_paths)
        return non_causal_paths

    def generate_non_causal_path(self, path_length, **path):
        new_path = []
        for key, value in path.items():
            if key == 'path':
                new_path = value
                break
        max_length = self.msgservers_graph.max_path_length()
        for i in range(max_length):
            paths = self.remove_duplicates(
                self.get_weighted_paths_helper_shorter(
                    self.msgservers_graph.get_paths_with_length_between_range(i, max_length)))
            random.shuffle(paths)
            while len(paths) != 0:
                path = paths.pop()
                for edge in path[0]:
                    if edge in new_path or (len(new_path) > 0 and (
                            self.is_in_same_path(new_path[-1], edge) or new_path[-1][0] == edge[0])):
                        continue
                    else:
                        new_path.append(edge)
                        break
                if len(new_path) == path_length:
                    return new_path
        # print("selected path(doesn't have enough edges):", new_path)
        return None

    def is_in_same_path(self, first_edge, second_edge):
        return (self.msgservers_graph.has_path(first_edge[1], second_edge[0])
                or self.msgservers_graph.has_path(second_edge[1], first_edge[0]))

    def enhance_causality_property_set(self, paths):
        path_found = False
        message_printed = False
        new_paths = []
        if len(paths) == self.causality_count:
            return paths
        for p in paths:
            path_found = False
            for i in range(self.property_length, self.msgservers_graph.max_path_length()):
                potential_paths = self.get_weighted_paths_with_length(i)
                for potential_path in potential_paths:
                    if set(p).issubset(set(potential_path)):
                        if potential_path in new_paths: continue
                        new_path = potential_path if len(potential_path) == self.property_length else self.get_subpath(
                            p, potential_path, new_paths)
                        if new_path != []:
                            new_paths.append(new_path)
                            path_found = True
                            break
                if path_found: break
            if not path_found:
                if not message_printed:
                    message_printed = not message_printed
                    print(colored(
                        "There wasn't enough edge to generate complete causal properties, so causal properties contain some non causal edges.",
                        'yellow'))
                new_path = self.create_semi_causal_path(p[:], new_paths)
                new_paths.append(new_path)
        self.causality_msgservers = new_paths
        print("\ncausal paths", self.causality_msgservers)
        causality_set = remove_duplicates_array([self.fix_format(p) for p in self.choose_causality_property_set()])
        self.causality_set = causality_set
        print("\nCausal properties", causality_set)
        return causality_set

    def create_semi_causal_path(self, path, paths):
        round = 0
        while round != 30:
            new_path = self.add_edges_to_complete(path, self.property_length)
            if not new_path in paths:
                return new_path
            round += 1
        assert False, "cannot generate proper path based on current path {}".format(path)

    def get_subpath(self, path, potential_path, new_paths):
        endges_in_path_indices = [i for i, val in enumerate(potential_path) if val in set(path)]
        endges_not_in_path_indices = [i for i, val in enumerate(potential_path) if val not in set(path)]
        for indices in itertools.combinations(endges_not_in_path_indices, self.property_length - len(path)):
            path_indices = sorted(endges_in_path_indices + indices)
            new_path = [potential_path[i] for i in path_indices]
            if new_path not in new_paths:
                return new_path
        return []

    def choose_causality_property_set(self):
        if self.causality_count == 0: return []
        selected_paths = self.causality_msgservers
        causality_count = self.causality_count - len(selected_paths)
        round = 0
        while causality_count != 0:
            if self.property_length == round:
                assert False, 'It has generated {} causal properties. Maybe property_length or causality_count values are too big for this graph.'.format(
                    len(selected_paths))
            weighted_paths = [(self.add_edges_to_complete(p, self.property_length), w) for p, w in
                              self.remove_duplicates(self.get_weighted_paths(self.property_length - round + 1))]
            weighted_paths = [(p, w) for p, w in weighted_paths if len(p) == self.property_length]
            if len(weighted_paths) == 0:
                round += 1
                continue
            if len(weighted_paths) >= causality_count:
                if round != 0:
                    print(colored(
                        "There wasn't enough edge to generate complete causal properties, so causal properties contain some non causal edges.",
                        'yellow'))
                selected_paths.extend(
                    [p for p in weighted_random_choices(weighted_paths, causality_count) if p not in selected_paths])
                return selected_paths
            else:
                new_paths = [p for p, w in weighted_paths if p not in selected_paths]
                selected_paths.extend(new_paths)
                causality_count -= len(new_paths)
            round += 1
        print(colored(
            "There wasn't enough edge to generate complete causal properties, so causal properties contain some non causal edges.",
            'yellow'))
        return selected_paths

    def add_edges_to_complete(self, path, total_length):
        if len(path) == total_length:
            return path
        all_edges = self.msgservers_graph.all_paths_with_length(2)
        for i in range(total_length - len(path)):
            random.shuffle(all_edges)
            for edge in all_edges:
                if edge in path or self.is_in_same_path(path[-1], edge) or path[-1][0] == edge[0]: continue
                path.append(edge)
                break
        return path

    def remove_duplicates(self, weighted_paths):
        def sortSecond(val):
            return val[1]

        weighted_paths.sort(key=sortSecond, reverse=True)
        # print('sorted', weighted_paths)
        seen = set()

        def seen_cond(_x):
            x = tuple(_x)
            return not (x in seen or seen.add(x))

        return [(a, b) for a, b in weighted_paths if seen_cond(a)]

    def get_weighted_paths_with_length(self, length):
        equal_or_longer_paths = self.msgservers_graph.all_paths_with_length_more_equal(length)
        return [cp for (cp, length) in self.get_weighted_paths_helper(equal_or_longer_paths, length)]

    def get_weighted_paths(self, path_length_needed):
        equal_or_longer_paths = self.msgservers_graph.all_paths_with_length_more_equal(path_length_needed)
        # print('equal_or_longer_paths', equal_or_longer_paths)

        shorter_paths = self.msgservers_graph.all_paths_with_length_in_range(path_length_needed, 2)

        res_shorter = self.get_weighted_paths_helper_shorter(shorter_paths)
        res = self.get_weighted_paths_helper(equal_or_longer_paths, path_length_needed)

        # print('res', res)
        # print('res_shorter', res_shorter)
        return res + res_shorter

    def get_weighted_paths_helper(self, equal_or_longer_paths, path_length_needed):
        # Generates paths with length == path_length_needed
        # output is [([subpath], length_of_path)]
        # if path_length_needed = 2,
        # output of [1,2,3] is [([1,2], 3), ([1,3], 3), ([2,3], 3)]
        # output of [1,2] is [([1,2], 2)]
        res = flatten_list([[(cp, len(p)) for cp in [
            list(x) for x in list(
                itertools.combinations(pairwise(p), path_length_needed - 1))
        ]] for p in equal_or_longer_paths])

        return res

    def get_weighted_paths_helper_shorter(self, shorter_paths):
        res = [(pairwise(p), len(p)) for p in shorter_paths]

        return res

    def convert_edge_to_property_seq(self, edge):
        return (name_gen.get_rebeca_name_of_msgserver(edge[0]), edge[1],
                name_gen.get_rebeca_name_of_msgserver(edge[1]))

    def write_in_json(self, json_output_file):
        # print()
        # print('self.causality_set',self.causality_set)
        # print(self.non_causality_set)
        # print()
        json_output_file.write('"casuality sequences": {},\n'.format(
            repr([['"{}"'.format(tuple_to_string(p)) for p in x] for x in self.causality_set]).replace('\'', '')))
        json_output_file.write('"casuality msgservers": {},\n'.format(
            repr([['"{}"'.format(tuple_to_string(p)) for p in x] for x in self.causality_msgservers]).replace('\'',
                                                                                                              '')))

        json_output_file.write('"non casuality sequences": {},\n'.format(
            repr([['"{}"'.format(tuple_to_string(p)) for p in x] for x in self.non_causality_set]).replace('\'', '')))
        json_output_file.write('"non casuality msgservers": {},\n'.format(
            repr([['"{}"'.format(tuple_to_string(p)) for p in x] for x in self.non_causality_msgservers]).replace('\'',
                                                                                                                  '')))
        json_output_file.write('"Deadlock sequences": {},\n'.format(
            repr([['"{}"'.format(tuple_to_string(p)) for p in x] for x in self.deadlock_property]).replace('\'', '')))

        json_output_file.write('"Deadlock sequences msgservers": {},\n'.format(
            repr([['"{}"'.format(tuple_to_string(p)) for p in x] for x in self.deadlock_property_msgservers]).replace('\'', '')))

        json_output_file.write('"repetitive Deadlock sequences": {},\n'.format(
            repr([['"{}"'.format(tuple_to_string(p)) for p in x] for x in self.repetitive_deadlock]).replace('\'', '')))


