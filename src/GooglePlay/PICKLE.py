
import os.path
import pickle

class PICKLE:
    def __init__(self, fName):
        self.fName = fName

    def dump(self, data):
        with open(self.fName, 'wb') as f:
            pickle.dump(data, f)

    def load(self):
        if os.path.isfile(self.fName):
            with open(self.fName, 'rb') as f:
                data = pickle.load(f)
        else: data = None

        return data
