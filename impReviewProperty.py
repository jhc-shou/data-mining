class ReviewProperty:
    def __init__(self):
        self.__ecSite = ''
        self.__dictComm = dict()

    # Set EC sit
    def setECSite(self, ecSite):
        self.__ecSite = ecSite

    # Get EC site
    @property
    def getECSite(self):
        return self.__ecSite

    # Get selector for EC site
    @property
    def getSiteSelector(self):
        if self.__ecSite == 'rakuten':
            return 'rakutenSelectors.yml'
        elif self.__ecSite == 'amazon':
            return 'amazonSelectors.yml'

    # Set dictionary of review from EC site
    def setDictComm(self, dictComm):
        self.__dictComm = dictComm

    # Get dictionary of review from EC site
    @property
    def getDictComm(self):
        return self.__dictComm
