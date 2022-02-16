import json
from rebec_program.rebec_program_conf import rebec_program_conf


class JsonHandler():
    def __init__(self, json_input_file):
        self.json_input_file = json_input_file
        
    def read_file(self, file_name):
        return json.load(open(file_name, 'r'))

    def read_input_json(self, *argv):
        input_file = argv[0] if len(argv) > 0 else self.json_input_file
        file_json = open(input_file, 'r')
        # json_string = file_json.read()
        # print('test', json_string)
        json_out = json.load(file_json)
        # print(json_out)
        return rebec_program_conf(
            json_out['rebec_count'], json_out['max_msgservers_count'],
            json_out['max_msgservers_seq'], json_out['property_length'],
            json_out['non_causality_count'], json_out['causality_count'],
            json_out['backwards_count'], json_out['maximum_method_calls'],
            json_out['deadlock_count'], json_out['deadlock_length'],
            json_out['strictly'])
