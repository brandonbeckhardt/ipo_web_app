from Parsers import MarketWatchParser
from Parsers import BloombergParser
import json
# import os
import re
import threading
import time


class KeyWordSearcher:
	def __init__(self, text_input,search_future):
		self.search_future = search_future
		self.ipos = MarketWatchParser().ipos
		self.keyWords = self.getKeyWords(text_input)
		self.matches = None
		self.getMatches()

	def getKeyWords(self, text_input):
		words = []
		if text_input:
			for word in re.split(';|,|\n',text_input.strip()):
				formattedWord = word.strip().lower().replace("~+~"," ")
				if formattedWord not in words:
					words.append(formattedWord)
		return words

	#Worked method for thread
	def getParsedData(self,group,company_info):
		company_name = company_info[0]
		ticker = company_info[1]
		bloombergParser = BloombergParser()
		content = bloombergParser.getDescription(ticker)
		
		company_map = None
		has_matched = False
		if content:
			description = content.strip()
			lowerCaseDescription = description.lower()
			for keyWord in self.keyWords:
				if lowerCaseDescription.find(keyWord) > -1:
					if has_matched:
						company_map['keyWordMatches'] = company_map['keyWordMatches'] + [keyWord]
					else:
						company_map = {'company_name':company_name,'keyWordMatches':[keyWord],'description':description}
						has_matched = True
		if has_matched:
			self.matches[group].append(company_map)
		return


	def getMatches(self):
		if not self.keyWords or len(self.keyWords) <= 0:
			return None
		else:
			self.matches = {}
			for group in self.ipos.keys():
				if group == 'this_week' or group =='next_week' or (group=='future' and self.search_future):
					self.matches[group] = []
					# create pool					    
					threads = []  
					for idx, company_info in enumerate(self.ipos[group]):
						t = threading.Thread(name='Company Info Fetcher',target=self.getParsedData,args=(group,company_info))
						threads.append(t)
						t.start()	
					for t in threads:
						t.join()
		return

	# k = KeyWordSearcher("a",True)

	# def printMatches(self):
	# 	for group in self.matches.keys():
	# 		print group
	# 		print "-------------------------"
	# 		for company in self.matches[group]:
	# 			print company + ": " + str(self.matches[group][company]['keyWordMatches'])
	
	# def outputToFile(self):
	# 	with open('keyWordResults.txt', 'w') as outfile:
	# 		json.dump(self.matches, outfile,indent=4, sort_keys=True)




