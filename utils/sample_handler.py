class SampleHandler():
    def __init__(self, json_handler, parser):
        self.json_handler = json_handler
        self.parser = parser
        self.config = self.json_handler.read_input_json()
        self.sample_config = self.json_handler.read_input_json(self.parser.get_sample_input())

    def program_is_different(self):
        return (
            (self.config.rebec_count != self.sample_config.rebec_count) or 
            (self.config.max_msgservers_count != self.sample_config.max_msgservers_count) or 
            (self.config.max_msgservers_seq != self.sample_config.max_msgservers_seq) or 
            (self.config.backwards_count != self.sample_config.backwards_count) or 
            (self.config.maximum_method_calls != self.sample_config.maximum_method_calls)
        )

    def deadlock_deadlock_properties_are_different(self):
        return (
            (self.config.deadlock_length != self.sample_config.deadlock_length) or
            (self.config.deadlock_count != self.sample_config.deadlock_count)
        )

    def deadlock_count_properties_are_different(self):
        return self.config.deadlock_count != self.sample_config.deadlock_count

    def deadlock_length_properties_are_different(self):
        return self.config.deadlock_length != self.sample_config.deadlock_length

    def properties_are_different(self):
        return (
            (self.config.property_length != self.sample_config.property_length) or
            (self.config.non_causality_count != self.sample_config.non_causality_count) or
            (self.config.deadlock_count != self.sample_config.deadlock_count) or
            (self.config.deadlock_length != self.sample_config.deadlock_length) or
            (self.config.causality_count != self.sample_config.causality_count)
        )

    def both_program_and_properties_are_different(self):
        return self.properties_are_different() and self.program_is_different()

    def both_inputs_are_the_same(self):
        return (
            (self.config.rebec_count == self.sample_config.rebec_count) and
            (self.config.max_msgservers_count == self.sample_config.max_msgservers_count) and
            (self.config.max_msgservers_seq == self.sample_config.max_msgservers_seq) and
            (self.config.backwards_count == self.sample_config.backwards_count) and
            (self.config.maximum_method_calls == self.sample_config.maximum_method_calls) and
            (self.config.property_length == self.sample_config.property_length) and
            (self.config.non_causality_count == self.sample_config.non_causality_count) and
            (self.config.deadlock_count == self.sample_config.deadlock_count) and
            (self.config.deadlock_length == self.sample_config.deadlock_length) and
            (self.config.causality_count == self.sample_config.causality_count)
        )

    def get_sample_dfa(self):
        sample_dfa = self.parser.get_sample_dfa()
        sample_directory = self.parser.get_sample_dir()
        assert (sample_dfa or sample_directory), "a dfa file or a directory must be set in order to get properties"
        return self.json_handler.read_file(sample_dfa if sample_dfa else self.parser.get_sample_dfa_from_directory(sample_directory))

    def sample_property_length_is_logner(self):
        return self.config.property_length < self.sample_config.property_length

    def sample_non_causals_count_is_bigger(self):
        pass
