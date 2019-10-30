import datetime

class PRISMDownloader:
    def __init__(self, var, res, year=None, month=None, day=None, normals=False):
        self.vars = ['ppt', 'tmin', 'tmax', 'tmean']
        self.var = self.checkVar(var)
        self.res = self.checkResolution(res)
        self.min_year = 1895  # earliest year data are available
        self.hist_year = 1981  # less than this retrieve historical data
        self.year = self.checkYear(year)
        self.month = self.checkMonth(month)
        self.day = self.checkDay(day)
        self.normals = normals
        self.url = None
        self.url_base = 'http://services.nacse.org/prism/data/public/'

    def buildURL(self):
        if self.normals:
            if self.month is None:
                raise Exception('Must specify a month to download normals')
            else:
                self.url = self.url_base + 'normals/' + self.res + "/" + self.var + "/" + self.month
        else:
            if self.year != '' and int(self.year) >= self.hist_year:
                self.url = self.url_base + "/" + self.res + "/" + self.var + "/" + self.year + self.month + self.day
            elif int(self.year) < self.hist_year:
                self.url = self.url_base + "/" + self.res + "/" + self.var + "/" + self.year
            else:
                raise Exception('A valid year must be specified')

    def checkDay(self, day):
        if day is None:
            return ''
        else:
            if type(day) != int or (day < 1 or day > 31):
                raise Exception("Day value must be an integer between 1 and 31")
            else:
                return str(day).zfill(2)

    def checkMonth(self, month):
        if month is None:
            return ''
        else:
            if type(month) != int or (month > 12 or month < 1):
                raise Exception("Month value must be an integer between 1 and 12")
            else:
                return str(month).zfill(2)

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

    def checkYear(self, year):
        if year is None:
            return ''
        else:
            if year < self.min_year:
                raise Exception("Year must not be earlier than {}".format(self.min_year))
            elif year > int(datetime.datetime.now().year):
                raise Exception("Year cannot be greater than the current year")
            else:
                return str(year)

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
