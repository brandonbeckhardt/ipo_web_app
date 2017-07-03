import json
import time
from DateHandling import DateHandling
from Enums import DateGroupNames
from Enums import UrlTypes

import logging


class UrlHandler:
	def __init__(self, urlRows, logger):
		self.urlRows = urlRows
		self.logger = logger
		self.privateCompanyUrls = {}
		self.publicCompanyUrls = {}
		self.brokerUrls = {}
		self.otherUrls = {}

		self.handleUrls()


	def handleUrls(self):
		for row in self.urlRows:
			if row.type == UrlTypes.PUBLIC_COMPANY_URL['enum']:
				self.publicCompanyUrls[row.reference_id] = row
			elif row.type == UrlTypes.PRIVATE_COMPANY_URL['enum']:
				self.privateCompanyUrls[row.reference_id] = row
			elif row.type == UrlTypes.BROKER_URL['enum']:
				self.brokerUrls[row.reference_id] = row

	def getCompanyUrl(self, group, match):
		url = ""
		if match.companyId in self.publicCompanyUrls and self.publicCompanyUrls[match.companyId].url != "":
			url = self.publicCompanyUrls[match.companyId].url
		elif match.companyId in self.privateCompanyUrls:
			url = self.privateCompanyUrls[match.companyId].url

		if url != "":
			if (url[:4] != 'http' and url[:5] != 'https'):
				if (url[:4] == 'www.'):
					url = "http://" + url
				else:
					url = "http://www." + url
		return url



