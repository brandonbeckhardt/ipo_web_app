class MatchObject:
	def __init__(self, companyInfo, keyWords):
		self.companyName = None
		self.ticker = None
		self.description = None
		self.companyId = None
		self.keyWordMatches = None
		self.ipoDate = None

		self.populateInfo(companyInfo, keyWords)

	def populateInfo(self, companyInfo, keyWords):
		self.companyName = companyInfo.company_info.name
		self.ticker = companyInfo.company_info.ticker
		self.description = companyInfo.company_info.description
		self.companyId = companyInfo.company_info.uuid
		self.keyWordMatches = keyWords
		self.ipoDate = companyInfo.ipo_info.date