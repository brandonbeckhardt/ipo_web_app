import requests
from HTMLParser import HTMLParser
import sys

# create a subclass and override the handler methods
class MarketWatchParser(HTMLParser):

	def __init__(self):
		HTMLParser.__init__(self)
		self.in_this_week_table = False
		self.in_next_week_table = False
		self.in_future_table = False

		self.data_is_this_week = False
		self.data_is_next_week = False
		self.data_is_future = False

		self.ticker_is_this_week = 0
		self.ticker_is_next_week = 0
		self.ticker_is_future = 0

		self.ipos ={'this_week':[],'next_week':[], 'future':[]}

		page = requests.get('http://www.marketwatch.com/tools/ipo-calendar')
		contents = page.content
		print 'contents ='
		print contents
		self.feed(contents)
		print self.ipos

	def handle_starttag(self, tag, attrs):
		attributes =  dict(attrs)
		attributeKeys = attributes.keys()
		if 'id' in attributeKeys and 'class' in attributeKeys:
			if attributes['id'] =='thisweek' and attributes['class']=='tablesorter':
				self.in_this_week_table = True
			elif attributes['id'] =='nextweek' and attributes['class']=='tablesorter':
				self.in_next_week_table = True
			elif attributes['id'] =='future' and attributes['class']=='tablesorter':
				self.in_future_table = True

		if tag == 'a' and self.in_this_week_table:
			self.data_is_this_week = True
		elif tag == 'a' and self.in_next_week_table:
			self.data_is_next_week = True
		elif tag == 'a' and self.in_future_table:
			self.data_is_future = True

	def handle_endtag(self, tag):
		if tag == 'table' and self.in_this_week_table:
			self.in_this_week_table = False
		if tag == 'table' and self.in_next_week_table:
			self.in_next_week_table = False
		if tag =='table' and self.in_future_table:
			self.in_future_table = False

	def addCompanyNameToIpos(self, label, data):
		self.ipos[label].append((data,None))
		setattr(self, 'data_is_'+label,False)
		setattr(self, 'ticker_is_'+label,1)

	def addTickerToIpos(self, label, data):
		if getattr(self,'ticker_is_'+label) == 2:
				self.ipos[label][len(self.ipos[label])-1] = (self.ipos[label][len(self.ipos[label])-1][0],data.strip())
				setattr(self, 'ticker_is_'+label, 0)
		else:
			setattr(self, 'ticker_is_'+label, getattr(self,'ticker_is_'+label)+1)

	def handle_data(self, data):
		if self.data_is_this_week:
			self.addCompanyNameToIpos('this_week',data)
		elif self.data_is_next_week:
			self.addCompanyNameToIpos('next_week',data)
		elif self.data_is_future:
			self.addCompanyNameToIpos('future',data)


		elif self.ticker_is_this_week>0:
			self.addTickerToIpos('this_week',data)
		elif self.ticker_is_next_week>0:
			self.addTickerToIpos('next_week',data)
		elif self.ticker_is_future>0:
			self.addTickerToIpos('future',data)

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













