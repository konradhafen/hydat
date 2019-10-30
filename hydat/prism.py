

class PRISMDownloader:
    def __init__(self, var, res, year=None, month=None, day=None, normals=False):
        self.vars = ['ppt', 'tmin', 'tmax', 'tmean']
        self.var = self.checkVar(var)
        self.res = self.checkResolution(res)
        self.min_year = 1895  # earliest year data are available
        self.hist_year = 1981  # less than this retrieve historical data
        self.year = year
        self.month = month
        self.day = day
        self.normals = normals
        self.url = None
        self.url_base = 'http://services.nacse.org/prism/data/public/'

    def buildURL(self):
        if self.normals:
            self.url = self.url_base + 'normals/'
            if self.month is None:
                raise Exception('Must specify a month to download normals')
            else:
                self.url = self.url + self.res + "/" + self.var + "/" + str(self.month).zfill(2)

    def checkResolution(self, res):
        if res is 800 or res is '800m':
            return '800m'
        elif res is 4 or res is '4km':
            return '4km'
        else:
            raise Exception('Please enter a valid resolution value, options are 800m or 4km')

    def checkVar(self, var):
        if var in self.vars:
            return var
        else:
            raise Exception('Please enter a valid variable, options are: {}'.format(self.vars))

    def setHistoricalYear(self, year):
        """
        Sets the first year regular data are available
        Args:
            year: 4-digit year

        Returns:

        """
        self.hist_year = year

    def setNormals(self, normals):
        """
        Set variable that determines if normals will be downloaded
        Args:
            normals: bool

        Returns:

        """
        if type(normals) == bool:
            self.normals = normals
        else:
            raise TypeError("Must use boolean value to set normals")
