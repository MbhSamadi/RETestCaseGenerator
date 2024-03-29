from utils.utils import flatten_list
from ast_decl.class_decl import class_decleration
from ast_decl.msgserver_decl import msgserver_decleration
from utils.writer import writer
from ast_decl.main_decl import main_decleration
from ast_decl.state_vars_decl import state_var_decleration
from utils.name_gen import name_gen
import random
import os

buffer_size_extra_space = 10


class ast_gen():
    def __init__(self, rebecas_graph, msgservers_graph, ast_config, deadlock_property_msgservers):
        self.rebecas_graph = rebecas_graph
        self.msgservers_graph = msgservers_graph
        self.class_declerations = []
        self.leaves = self.msgservers_graph.get_leaves()
        self.self_call_deadlock_property = self.extract_self_call_deadlock_property(deadlock_property_msgservers)
        # print('Rebecas', self.rebecas_graph)
        # print('self_call_deadlock_property', self.self_call_deadlock_property)
        # print("leaves", self.leaves)

    def extract_self_call_deadlock_property(self, deadlock_property_msgservers):
        self_call_prp = set()
        for path in deadlock_property_msgservers:
            for prp in path:
                self_call_prp.add(prp[0])
        return list(self_call_prp)

    def generate(self):
        for rebeca in list(self.rebecas_graph.get_nodes()):
            class_decl = self.create_class_decleration(rebeca)
            self.add_msgservers_of_rebec(
                class_decl, rebeca, class_decl.state_vars)
            self.class_declerations.append(class_decl)

        self.main_decleration = main_decleration(self.class_declerations)
        # print(self.class_declerations)

    def create_class_decleration(self, rebeca):
        state_vars = self.create_random_state_vars()
        buffer_size = len(
            self.rebecas_graph.nodes_that_connect_to(rebeca)) + buffer_size_extra_space
        known_rebecs = self.rebecas_graph.edges(rebeca)
        return class_decleration(
            rebeca,
            buffer_size,
            known_rebecs,
            state_vars
        )

    def create_random_state_vars(self):
        state_vars_number = random.randint(1, 3)
        return [state_var_decleration(sv, random.choice(['int', 'boolean'])) for sv in random.sample(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l'], state_vars_number)]

    def get_msgservers_of_rebeca(self, rebeca):
        return [msgs for msgs in self.msgservers_graph.get_nodes() if str(name_gen.get_rebeca_name_of_msgserver(msgs)) == str(rebeca)]

    def remove_if_exsit_in_edges(self, elements, edges):
        res = []
        for edge in edges:
            if edge not in elements:
                res.append(edge)
        return res


    def add_msgservers_of_rebec(self, class_decl, rebeca, state_vars):
        msg_servers = self.get_msgservers_of_rebeca(rebeca)
        for msgs in msg_servers:
            edges = self.remove_if_exsit_in_edges(self.self_call_deadlock_property, self.msgservers_graph.edges(msgs))
            msgs_decl = msgserver_decleration(
                rebeca, msgs, edges, state_vars)

            class_decl.add_msgserver(msgs_decl)
            if msgs in self.leaves or msgs in self.self_call_deadlock_property:
                class_decl.add_call_msgserver_in_constructor(msgs_decl)

    def export_dot_rebec_file(self, folder):
        for c_decl in self.class_declerations:
            c_decl.write()

        self.main_decleration.write()

        writer.close()

        os.rename("output.rebec", "{}/output.rebec".format(folder))
