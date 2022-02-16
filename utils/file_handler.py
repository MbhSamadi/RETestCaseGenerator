import os
from datetime import datetime

class FileHandler():
    def __init__(self, folder_address='outputs'):
        self.folder_address = folder_address
        if not os.path.exists(self.folder_address):
            os.makedirs(self.folder_address)

    def mkdir(self):
        self.folder = '{}/{}'.format(self.folder_address, datetime.now().strftime("%d-%m-%Y-%H-%M-%S"))
        os.makedirs(self.folder)
        
    
        
