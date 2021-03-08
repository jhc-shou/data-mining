class ReviewProperty:
    def __init__(self):
        self.ecSite = ''
        self.dictComm = dict()

    # Set EC site
    def setECSite(self, ecSite):
        self.ecSite = ecSite

    # Get EC site
    def getECSite(self):
        return self.ecSite

    # Get selector for EC site
    def getSiteSelector(self):
        if self.ecSite == 'rakuten':
            return 'rakutenSelectors.yml'
        elif self.ecSite == 'amazon':
            return 'amazonSelectors.yml'

    # Set dictionary of review from EC site
    def setDictComm(self, dictComm):
        self.dictComm = dictComm

    # Get dictionary of review from EC site
    def getDictComm(self):
        return self.dictComm
