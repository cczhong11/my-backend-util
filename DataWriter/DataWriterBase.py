class DataWriterBase(object):
    def __init__(self):
        pass
    
    def write_data(self, path, data):
        return 0

    def health_check(self)->bool:
        return True