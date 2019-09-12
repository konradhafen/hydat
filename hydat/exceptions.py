class InvalidExtent(Exception):
    def __init__(self, msg):
        self.msg = msg

    def print_exception(self):
        print("Invalid Extent: ", self.msg)
