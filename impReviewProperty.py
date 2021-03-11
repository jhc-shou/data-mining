class ReviewProperty:
    def __init__(self):
        self.ecSite = ''
        self.dictComm = dict()

    # Set EC sit
    def setECSite(self, ecSite):
        self.ecSite = ecSite

    # Get EC site
    @property
    def getECSite(self):
        return self.ecSite

    # Get selector for EC site
    @property
    def getSiteSelector(self):
        if self.ecSite == 'rakuten':
            return 'rakutenSelectors.yml'
        elif self.ecSite == 'amazon':
            return 'amazonSelectors.yml'

    # Set dictionary of review from EC site
    def setDictComm(self, dictComm):
        self.dictComm = dictComm

    # Get dictionary of review from EC site
    @property
    def getDictComm(self):
        return self.dictComm
