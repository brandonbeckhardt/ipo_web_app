import requests
from HTMLParser import HTMLParser
import sys
import json
import threading
import time
from DateHandling import DateHandling


class CompanyInformationFetcher:
	def __init__(self, ipos):
		self.ipos = ipos
		self.getCompanyInfo()
		# self.getCompanyInfo()

	def getParsedData(self,group,company_info):
		company_name = company_info[0]
		ticker = company_info[1]
		bloombergParser = BloombergParser()
		content = bloombergParser.getDescription(ticker)

		if content:
			description = content.strip()
			company_map = {"ticker":ticker,"description":description, "company_name":company_name}
			self.companies[group].append(company_map)
		return

	def getCompanyInfo(self):
		print 'Getting company info..'
		self.companies={}
		# create pool		
		threads = []
		for row in self.ipos:
			group = DateHandling.getGroupFromDate(row.ipo_info.date_week)
			if group == 'this_week' or group =='next_week' or group=='future':
				self.companies[group] = []
				companyInfo =  (row.company_info.name,row.ipo_info.intended_ticker)			    
				t = threading.Thread(name='Company Info Fetcher',target=self.getParsedData,args=(group,companyInfo))
				threads.append(t)
				t.start()	
			for t in threads:
				t.join()



class BloombergParser(HTMLParser):
	def getDescription(self, ticker):
		self.in_description_paragraph = False
		self.description = None
		try:
			page = requests.get("https://www.bloomberg.com/quote/"+ticker+":US")
			contents= page.content
			self.feed(contents)
			return self.description
		except:
			print("Unexpected error:", sys.exc_info()[0])
    		return None
		
	def handle_starttag(self, tag, attrs):
		for attribute in attrs:
			if attribute[0] == 'class' and attribute[1] =='profile__description':
				self.in_description_paragraph = True

	def handle_endtag(self, tag):
		if tag == 'div' and self.in_description_paragraph:
			self.in_description_paragraph = False

	def handle_data(self, data):
		if self.in_description_paragraph:
			self.description = data













