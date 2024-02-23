
from pathlib import Path
import numpy as np

class Lickcalc:
    def __init__(self, **kwargs):
        ## Set default parameters

        if "longlick_threshold" in kwargs:
            self.longlick_threshold = kwargs['longlick_threshold']
        else:
            self.longlick_threshold = 0.5
        

        ## Read in and process data
        self.licks = np.array(kwargs.get('licks', None))

        if "offset" in kwargs:
            self.offset = np.array(kwargs['offset'])
            self.calc_long_licks()
        else:
            self.offset = None
            self.licklength = None
            self.longlicks = None



        print(self.longlicks)


    def calc_long_licks(self):
        full_licks = self.licks[:len(self.offset)]
        self.licklength = self.offset - full_licks
        if min(self.licklength) < 0:
            print("Some offsets precede onsets. Not doing lick length analysis.")
            self.licklength = None
            self.longlicks = None
        else:
            self.longlicks = [x for x in self.licklength if x > self.longlick_threshold]

        print("hey")


        







if __name__ == '__main__':
    print('Testing functions')
    import trompy as tp
    filename = Path("C:/Users/jmc010/Github/trompy/tests/test_data/03_W.med")

    data = tp.medfilereader(filename, vars_to_extract=["e", "f"], remove_var_header=True)

    lickdata = Lickcalc(licks=data[0], offset=data[1])


    lickdata = Lickcalc()


    lickdata = Lickcalc(licks="hello")
