import datetime
import os
import ftplib
import zipfile
import wget


class PRISMDownloader:
    def __init__(self):
        self.vars = ['ppt', 'tmin', 'tmax', 'tmean']
        self.var = None
        self.res = None
        self.min_year = 1895  # earliest year data are available
        self.hist_year = 1981  # less than this retrieve historical data
        self.mversion = None
        self.is_historical = None
        self.year = None
        self.month = None
        self.day = None
        self.normals = None
        self.url = None
        self.url_base = 'http://services.nacse.org/prism/data/public/'
        self.fnbase = 'PRISM'
        self.fn = None
        self.ftp = None

    def buildFTPFilename(self):
        allvar = ''
        monthvar = ''
        if self.is_historical:
            if self.var == 'ppt':
                self.mversion = 'M2'
            allvar = '_all'
        else:
            self.mversion = 'M3'
            monthvar = self.month
        self.fn = self.fnbase + '_' + self.var + '_stable_' + self.res + self.mversion + '_' + \
                      self.year + monthvar + allvar + '_bil.zip'

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

    def changeCWD_FTP(self):
        if self.normals:
            wd = 'normals_' + self.res + '/' + self.var
        elif self.day == '':
            wd = 'monthly/' + self.var + '/' + self.year
        else:
            wd = 'daily/' + self.var + '/' + self.year

        self.ftp.cwd(wd)

    def downloadFTP(self, var, dirname=None, res='4km', year=None, month=None, day=None, normals=False, extract=True,
                    remove_zip=True, overwrite=True):
        if self.ftp is None:
            self.login()
        self.setProperties(var, res, year, month, day, normals)
        self.buildFTPFilename()
        self.changeCWD_FTP()
        if dirname is not None:
            os.chdir(dirname)
        file = open(self.fn, 'wb')
        self.ftp.retrbinary("RETR " + self.fn, file.write)
        file.close()
        self.ftp.cwd('/')
        if extract:
            self.extract(os.getcwd() + '/' + self.fn, dirname, remove_zip)

    def downloadWebServices(self, fn, var, res='4km', year=None, month=None, day=None, normals=False, overwrite=True,
                            extract=True, extract_dir=None, remove_zip=True):
        self.setProperties(var, res, year, month, day, normals)
        self.buildURL()
        if overwrite:
            if os.path.exists(fn):
                os.remove(fn)
        print(self.url)
        wget.download(self.url, fn)
        if extract:
            self.extract(fn, extract_dir, remove_zip)

    def extract(self, fn, dirname=None, remove_zip=True):
        if os.path.isfile(fn):
            if dirname is None:
                dirname = os.path.dirname(fn)
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            zfile = zipfile.ZipFile(fn, 'r')
            zfile.extractall(dirname)
            zfile.close()
            if remove_zip:
                os.remove(fn)
        else:
            raise FileExistsError('The file {} does not exist')

    def login(self):
        self.ftp = ftplib.FTP('prism.nacse.org')
        self.ftp.login('anonymous', 'email@email.com')

    def setDay(self, day):
        if day is None:
            self.day = ''
        else:
            if type(day) != int or (day < 1 or day > 31):
                raise Exception("Day value must be an integer between 1 and 31")
            else:
                self.day = str(day).zfill(2)

    def setHistoricalYear(self, year):
        """
        Sets the first year regular data are available
        Args:
            year: 4-digit year

        Returns:

        """
        self.hist_year = year

    def setMonth(self, month):
        if month is None:
            self.month = ''
        else:
            if type(month) != int or (month > 12 or month < 1):
                raise Exception("Month value must be an integer between 1 and 12")
            else:
                self.month = str(month).zfill(2)

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

    def setProperties(self, var, res, year, month, day, normals):
        self.setNormals(normals)
        self.setVar(var)
        self.setResolution(res)
        self.setYear(year)
        self.setMonth(month)
        self.setDay(day)

    def setResolution(self, res):
        if res is 800 or res is '800m':
            self.res = '800m'
        elif res is 4 or res is '4km':
            self.res = '4km'
        else:
            raise Exception('Please enter a valid resolution value, options are 800m or 4km')

    def setVar(self, var):
        if var in self.vars:
            self.var = var
        else:
            raise Exception('Please enter a valid variable, options are: {}'.format(self.vars))

    def setYear(self, year):
        if year is None:
            self.year = ''
            self.is_historical = None
        else:
            if year < self.min_year:
                raise Exception("Year must not be earlier than {}".format(self.min_year))
            elif year > int(datetime.datetime.now().year):
                raise Exception("Year cannot be greater than the current year")
            else:
                self.year = str(year)
                if year < self.hist_year:
                    self.is_historical = True
                else:
                    self.is_historical = False

def downloadMonthlyPRISM_FTP(start_year, end_year, output_dir, variables=()):
    downloader = PRISMDownloader()
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    os.chdir(output_dir)
    for var in variables:
        if not os.path.exists(var):
            os.mkdir(var)
        os.chdir(var)
        for year in range(start_year, end_year+1):
            if not os.path.exists(str(year)):
                os.mkdir(str(year))
            os.chdir(str(year))
            for month in range(1, 13):
                downloader.downloadFTP(var, year=year, month=month)
                if downloader.is_historical:
                    break
            os.chdir('../')
        os.chdir('../')
    os.chdir(output_dir)

