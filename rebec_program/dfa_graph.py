from utils.utils import tuple_to_string


class dfa_graph_gen():
    def __init__(self, dfa_obj, backwards, deadlock_property, strictly):
        self.states = dfa_obj['states']
        self.transitions = dfa_obj['transitions']
        self.input_symbols = dfa_obj['input_symbols']
        self.final_states = dfa_obj['final_states']
        self.initial_state = dfa_obj['initial_state']
        self.strictly = strictly

        self.deadlock_transition = self.extract_deadlock_transition(deadlock_property)
        self.set_cover_deadlock = self.extract_set_cover_deadlock(deadlock_property)

        self.backwards = backwards
        self.vio_paths = self.get_vio_paths()
        self.vio_paths_reveresed = self.get_vio_paths_reversed()

        print('backwards', self.backwards)
        print('vio_paths', self.vio_paths)
        print('vio_paths_reveresed', self.vio_paths_reveresed)

        self.get_input_edges_to_state_cache = dict({self.initial_state: {}})
        self.enriched_transitions = self.get_all_enriched_transitions()
        self.get_all_input_edges_to_state()


    def extract_set_cover_deadlock(self, deadlock_property):
        if self.strictly:
            return []

        new_format_deadlock_property = self.change_format(deadlock_property)
        flat_deadlock_property = [item for sublist in new_format_deadlock_property for item in sublist]
        unique_deadlock_property = list(set(flat_deadlock_property))
        number_of_unique_property = len(unique_deadlock_property)
        # print("deadlock_property",unique_deadlock_property)

        res = []

        for i in range(pow(number_of_unique_property, 2)):
            selected_properties = self.extracted_property_with_binary_selctor(i, unique_deadlock_property)

            res.append(self.is_satisfy_set_cover_prblem(new_format_deadlock_property, selected_properties))

        set_cover = unique_deadlock_property.copy()
        for i in range(pow(number_of_unique_property, 2)):
            if res[i]:
                temp = self.extracted_property_with_binary_selctor(i, unique_deadlock_property)
                if len(set_cover) > len(temp):
                    set_cover = temp

        print("set_cover", set_cover, "\n")

        return self.find_set_cover_transaction_in_deadlock(set_cover)

    def find_set_cover_transaction_in_deadlock(self,set_cover):
        res = []
        for item in set_cover:
            for dead_lock in self.deadlock_transition:
                if dead_lock[1] == item:
                    res.append(dead_lock)
        return res

    def is_satisfy_set_cover_prblem(self, deadlock_property, selected_properties):
        for deadlock_path in deadlock_property:
            check = any(item in selected_properties for item in deadlock_path)
            if not check:
                return False
        return True
    def extracted_property_with_binary_selctor(self, number, unique_deadlock_property):
        selected_property = []
        binary = bin(number)[2:].zfill(len(unique_deadlock_property))
        for select in range(len(unique_deadlock_property)):
            if binary[select] == "1":
                selected_property.append(unique_deadlock_property[select])
        return selected_property

    def extract_not_strictly_deadlock_property(self, deadlock_paths):
        deadlock_prop = []
        for deadlock_path in deadlock_paths:
            for i in range(1, len(deadlock_path)):
                deadlock_prop.append([deadlock_path[i - 1], deadlock_path[i]])
                if i == len(deadlock_path) - 1:
                    deadlock_prop.append([deadlock_path[i], deadlock_path[0]])
        return deadlock_prop

    def extract_deadlock_transition(self, deadlock_property):
        if not self.strictly:
            deadlock_property = self.extract_not_strictly_deadlock_property(deadlock_property)
        # print("deadlock_propertyuyyy", deadlock_property)
        # deadlock_property = self.extract_not_strictly_deadlock_property(deadlock_property)
        # print("deadlock_propertyuyyy", deadlock_property)
        deadlock_property_path = self.change_format(deadlock_property)

        # print("deadlock_property",deadlock_property)
        # print("deadlock_property_path",deadlock_property_path)

        deadlock_transition = []
        for s in self.states:
            for path in deadlock_property_path:
                if path[0] in self.transitions[s]:
                    deadlock_transition.extend(self.find_deadlock_path_in_dfa(s, path))
                    # print(s, self.transitions[s])
        # print("deadlock_property_path", deadlock_property_path)
        # print("deadlock_path",deadlock_path)

        print("deadlocks: ", deadlock_transition)
        print("")
        return deadlock_transition

    def change_format(self, path):
        property_path = []
        for proprty in path:
            temp_property = []
            for i in range(len(proprty)):
                pi = '-'.join(proprty[i])
                temp_property.append(pi)
            property_path.append(temp_property)
        return property_path

    def find_deadlock_path_in_dfa(self, s, deadlock_path):
        next_start_state = s
        deadlock_transitions = []
        for i in deadlock_path:
            if i in self.transitions[next_start_state]:
                deadlock_transitions.append((next_start_state, i, self.transitions[next_start_state][i]))
                next_start_state = self.transitions[next_start_state][i]
            else:
                return []
        if next_start_state in self.final_states:
            # print("yes", deadlock_transitions)
            return deadlock_transitions
        else:
            return []

    def is_transition_in_init_deadlock(self, transition):
        return transition in self.set_cover_deadlock

    def is_transition_in_deadlock(self, transition):
        return transition in self.deadlock_transition

    def get_all_enriched_transitions(self):
        transitions = []
        for s in self.states:
            for sym in self.transitions[s]:
                transitions.append((s, sym, self.transitions[s][sym]))

        return transitions

    def get_rebec_transitions(self, rebec):
        transitions = []

        for et in self.enriched_transitions:
            msg = et[1]
            if rebec == msg[:msg.find('-')]:
                transitions.append(et)
        # print(self.enriched_transitions, transitions, rebec)
        return transitions

    def get_pre_transitions(self, transition):
        qstart, msg, qend = transition
        if not self.is_backward(transition):
            return self.get_input_edges_to_state(qstart)
        else:
            input_transitions = self.get_input_edges_to_state(qstart)
            pre_vio = self.vio_paths_reveresed[tuple_to_string(transition)]
            # print(transition, input_transitions, pre_vio)
            return [p for p in pre_vio if p in input_transitions]

    def is_final_path(self, transition):
        return transition[2] in self.final_states

    def get_input_edges_to_state(self, state):
        if state in self.get_input_edges_to_state_cache:
            return self.get_input_edges_to_state_cache[state]

        ans = set()
        for s in self.states:
            for sym in self.transitions[s]:
                if self.transitions[s][sym] == state:
                    ans.add((s, sym, state))

        self.get_input_edges_to_state_cache[state] = ans
        return ans

    def get_all_input_edges_to_state(self):
        for s in self.states:
            for sym in self.transitions[s]:
                dest = self.transitions[s][sym]
                p = (s, sym, dest)
                if self.is_backward(p):
                    continue
                if dest in self.get_input_edges_to_state_cache:
                    self.get_input_edges_to_state_cache[dest].add(p)
                else:
                    self.get_input_edges_to_state_cache[dest] = set([p])

    def get_vio_transition(self, pre_repr):
        # pre_repr = repr(pre_path)
        # print('pre,vio', pre_repr, self.vio_paths)
        if pre_repr in self.vio_paths:
            return list(self.vio_paths[pre_repr])
        return []

    def is_backward(self, _t):
        t = tuple_to_string(_t)
        # print(t, self.vio_paths_reveresed, t in self.vio_paths_reveresed)
        return t in self.vio_paths_reveresed

    def get_vio_paths_reversed(self):
        vio_paths_reveresed = dict()
        # print(self.vio_paths)
        for pre in self.vio_paths:
            vio = self.vio_paths[pre]
            for dest in vio:
                if dest in vio_paths_reveresed:
                    vio_paths_reveresed[dest].add(pre)
                else:
                    vio_paths_reveresed[dest] = set([pre])

        # print(vio_paths_reveresed)
        return vio_paths_reveresed

    def get_vio_paths(self):
        vio_paths = dict()

        for b in self.backwards:
            paths = self.find_all_paths(b[2], b[0])
            # print('bac', b, paths)
            for p in paths:
                for t in p:
                    if t in vio_paths:
                        vio_paths[t].add(tuple_to_string(b))
                    else:
                        vio_paths[t] = set([tuple_to_string(b)])

        return vio_paths

    def get_direct_link(self, start, end):
        for sym in self.transitions[start]:
            if end in self.transitions[start][sym]:
                return sym

        return False

    def find_all_paths(self, start, end, path=[]):
        path = path + [start]

        sym = self.get_direct_link(start, end)
        if sym:
            return [[(start, sym, end)]]
        if not start in self.states:
            return []
        res = []
        for sym in self.transitions[start]:
            node = self.transitions[start][sym]
            if node not in path:
                newRes = self.find_all_paths(node, end, path)
                for r in newRes:
                    res.append([(start, sym, node)] + r)
        return res
