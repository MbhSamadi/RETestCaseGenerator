from utils.input_getter import input_getter
from rebec_program.msgserver_call_graph_gen import msgserver_call_graph_gen
from rebec_program.rebec_program_gen import rebec_program_gen
from utils.graph import graph
from utils.command_parser import CommandParser
from utils.file_handler import FileHandler
from rebec_program.rebeca_ast_config_gen import rebeca_ast_gen
from rebec_program.ast_gen import ast_gen
from rebec_program.property_gen import property_gen
from rebec_program.dfa_gen import dfa_gen
from rebec_program.table_gen import table_gen
from rebec_program.dfa_graph import dfa_graph_gen
#from rebec_program.draw_automata import draw_automata
from termcolor import colored
import shutil
import os
from datetime import datetime
import sys
from utils.json_handler import JsonHandler
from utils.sample_handler import SampleHandler
import re

class RebecaGenerator():
    def __init__(self):
        self.file_handler = FileHandler()
        self.parser = CommandParser(sys.argv[1:])
        self.json_handler = JsonHandler(self.parser.get_input())
        
    def run(self):
        self.file_handler.mkdir()
        shutil.copy(self.json_handler.json_input_file, self.file_handler.folder)
        self.configuration = self.json_handler.read_input_json() if self.json_handler.json_input_file else input_getter.get_configuration()
        if not self.parser.has_samples():
            self.run_without_sample()
        else:
            self.run_with_sample()

    def generate_output_rebec(self, rebecas_graph, msgservers_graph, deadlock_property_msgservers):
        rebeca_ast_generate = rebeca_ast_gen(rebecas_graph, msgservers_graph)
        ast_config = rebeca_ast_generate.generate_ast()
        ast_generator = ast_gen(rebecas_graph, msgservers_graph, ast_config, deadlock_property_msgservers)
        ast_generator.generate()
        ast_generator.export_dot_rebec_file(self.file_handler.folder)
        print()
        print(colored('Generated code is ready in output.rebec', 'magenta', attrs=['bold']))

    def generate_msgserver_and_rebecas_graph_generator(self):
        rebec_program_generator = rebec_program_gen(self.configuration)
        rebec_msgservers = rebec_program_generator.generate()
        msgserver_call_graph_generator = msgserver_call_graph_gen(self.configuration, rebec_msgservers)
        call_graph = msgserver_call_graph_generator.generate_graph()
        rebecas_graph, msgservers_graph = call_graph[1], call_graph[0]
        print(colored('Rebecas:', 'yellow', attrs=['bold']), rebecas_graph)
        print(colored('MsgServers:', 'yellow', attrs=['bold']), msgservers_graph)
        return rebecas_graph, msgservers_graph

    def make_json_output_file(self, rebecas_graph, msgservers_graph):
        json_output_file = open('{}/dfa.json'.format(self.file_handler.folder), 'w', newline='\n')
        json_output_file.write('{\n')
        json_output_file.write('"msgserver graph":' + repr(msgservers_graph)[6:].replace('\'', '\"') + ',\n')
        json_output_file.write('"rebeca graph":' + repr(rebecas_graph)[6:].replace('\'', '\"') + ',\n')
        return json_output_file

    def close_json_output_file(self, json_output_file):
        json_output_file.write('}\n')
        json_output_file.close()

    def fix_sequences(self, sequence):
        fixed = []
        for p in sequence:
            path = []
            for item in p:
                m = re.search('\((.+?),(.+?)\)', item)
                if m:
                    path.append((m.group(1), m.group(2)))
            fixed.append(path)
        return fixed

    def enhance_property_set(self, msgservers_graph, json_output_file, sample_dfa, sample_handler):
        property_generator = property_gen(msgservers_graph, sample_handler.sample_config)
        non_causals = property_generator.enhance_non_causality_property_set(self.fix_sequences(sample_dfa['non casuality msgservers']))
        causals = property_generator.enhance_causality_property_set(self.fix_sequences(sample_dfa['casuality msgservers']))
        property_set = causals + non_causals
        property_generator.write_in_json(json_output_file)
        print()
        print(colored('Property set:', 'yellow', attrs=['bold']), property_set)
        return property_set

    def enhance_deadlock_property_set(self, msgservers_graph, json_output_file, sample_dfa, sample_handler):
        property_generator = property_gen(msgservers_graph, sample_handler.sample_config)
        causals = self.fix_sequences(sample_dfa['casuality msgservers'])
        if sample_handler.deadlock_count_properties_are_different():
            non_causals = property_generator.enhance_deadlock_count_property_set(self.fix_sequences(sample_dfa['non casuality msgservers']),
                                                                             self.fix_sequences(sample_dfa['Deadlock sequences msgservers']),
                                                                             self.fix_sequences(sample_dfa['repetitive Deadlock sequences']),
                                                                                 )
        if sample_handler.deadlock_length_properties_are_different():
            non_causals = property_generator.enhance_deadlock_length_property_set(self.fix_sequences(sample_dfa['non casuality msgservers']),
                                                                             self.fix_sequences(sample_dfa['Deadlock sequences msgservers']),
                                                                             self.fix_sequences(sample_dfa['repetitive Deadlock sequences']),
                                                                                 )
        property_set = causals + non_causals
        property_generator.write_in_json(json_output_file)
        print()
        print(colored('Property set:', 'yellow', attrs=['bold']), property_set)
        deadlock_property = property_generator.get_deadlock_property()
        deadlock_property_msgservers = property_generator.get_deadlock_property_msgservers()
        return property_set, deadlock_property, deadlock_property_msgservers

    def generate_property_set(self, msgservers_graph, json_output_file):
        property_generator = property_gen(msgservers_graph, self.configuration)
        property_set = property_generator.get_property_set()
        deadlock_property = property_generator.get_deadlock_property()
        property_generator.write_in_json(json_output_file)
        deadlock_property_msgservers = property_generator.get_deadlock_property_msgservers()
        print()
        print(colored('Property set:', 'yellow', attrs=['bold']), property_set)
        return property_set, deadlock_property, deadlock_property_msgservers

    def generate_dfa_and_tables(self, rebecas_graph, property_set, deadlock_property, json_output_file):
        dfa_generator = dfa_gen(property_set, self.configuration)
        dfa_obj = dfa_generator.get_dfa()
        print()
        print(colored('DFA:', 'yellow', attrs=['bold']))
        dfa_generator.print_automata_obj(dfa_obj)
        dfa_generator.write_automata_obj(json_output_file, dfa_obj)

        dfa_graph = dfa_graph_gen(dfa_obj, dfa_generator.backwards, deadlock_property, self.configuration.strictly)
        table_generator = table_gen(rebecas_graph, dfa_graph, self.file_handler.folder)
        table_generator.export_table()
        # draw_automata(dfa_obj, folder)

    def run_without_sample(self):
        rebecas_graph, msgservers_graph = self.generate_msgserver_and_rebecas_graph_generator()
        json_output_file = self.make_json_output_file(rebecas_graph, msgservers_graph)
        property_set, deadlock_property, deadlock_property_msgservers = self.generate_property_set(msgservers_graph, json_output_file)
        self.generate_output_rebec(rebecas_graph, msgservers_graph, deadlock_property_msgservers)
        self.generate_dfa_and_tables(rebecas_graph, property_set, deadlock_property, json_output_file)
        self.close_json_output_file(json_output_file)

    def run_with_sample(self):
        deadlock_property = []
        deadlock_property_msgservers = []
        print('sample input:', self.parser.get_sample_input())
        sample_handler = SampleHandler(self.json_handler, self.parser)
        if sample_handler.both_program_and_properties_are_different() or sample_handler.both_inputs_are_the_same():
            self.run_without_sample()
            return
        elif sample_handler.properties_are_different():
            sample_dfa = sample_handler.get_sample_dfa()
            rebecas_graph, msgservers_graph = graph(sample_dfa['rebeca graph']), graph(sample_dfa['msgserver graph'])
            json_output_file = self.make_json_output_file(rebecas_graph, msgservers_graph)
            if sample_handler.deadlock_deadlock_properties_are_different():
                property_set, deadlock_property, deadlock_property_msgservers = self.enhance_deadlock_property_set(msgservers_graph, json_output_file,
                                                                            sample_dfa, sample_handler)
            else:
                property_set = self.enhance_property_set(msgservers_graph, json_output_file, sample_dfa, sample_handler)
            self.generate_output_rebec(rebecas_graph, msgservers_graph, deadlock_property_msgservers) # give deadlock to it
            self.generate_dfa_and_tables(rebecas_graph, property_set, deadlock_property, json_output_file) # give deadlock to it
            self.close_json_output_file(json_output_file)
            return
        elif sample_handler.program_is_different():
            print('program section')


if __name__ == "__main__":
    generator = RebecaGenerator()
    generator.run()
