import os

from src.utils import mkdir


class Logger():
    def __init__(self, session, test_directory, iteration, name, number,
                 stdout=False):
        self.session = session
        self.test_directory = test_directory
        self.iteration = iteration
        self.transformation_name = name
        self.transformation_number = number
        self.stdout = stdout
        if not self.stdout:
            self.directory = os.path.join(self.test_directory, "logs")
            mkdir(self.directory)
            self.filename = os.path.join(self.directory, str(self.iteration))

    def log_info(self):
        msg = "\n{}\nTransformation name:{}\nTransformation No: {}\n\n".format(
            10*"=",
            self.transformation_name,
            self.transformation_number
        )
        self.log(msg)

    def log(self, msg):
        if self.stdout:
            print(msg)
        else:
            with open(self.filename, 'a') as out:
                out.write(str(msg))
                out.write('\n')


def log(logger: Logger, msg: str):
    if logger is not None:
        logger.log(msg)
