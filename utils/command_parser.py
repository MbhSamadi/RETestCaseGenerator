commandsConstants = { 'INPUT': '-i', 'SAMPLE_INPUT': '-s', 'SAMPLE_REBEC': '-r', 'SAMPLE_DFA': '-d', 'SAMPLE_DIRECTORY' : '-D', 'SAMPLE_DFA_FILE_NAME': 'dfa.json'}

class CommandParser():

    def __init__(self, commands):
        self.commands = commands

    def get_input(self):
        input_file = self.get_command('INPUT')
        return input_file if input_file is not None else 'input.json'

    def get_command(self, command):
        try:
            index = self.commands.index(commandsConstants[command])
        except ValueError:
            return None
        return self.commands[index + 1] if len(self.commands) > (index + 1) else None

    def get_sample_dfa_from_directory(self, dir_name):
        return dir_name + '/' + commandsConstants['SAMPLE_DFA_FILE_NAME']

    def get_sample_input(self):
        return self.get_command('SAMPLE_INPUT')

    def get_sample_rebec(self):
        return self.get_command('SAMPLE_REBEC')

    def get_sample_dfa(self):
        return self.get_command('SAMPLE_DFA')

    def get_sample_dir(self):
        return self.get_command('SAMPLE_DIRECTORY')

    def has_samples(self):
        return True if self.get_sample_input() is not None else False
