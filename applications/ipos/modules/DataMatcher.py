import json
import re
import threading
import time
from DateHandling import DateHandling

import logging


class DataMatcher:
	def __init__(self, text_input,match_all,companies, logger):
		self.match_all=match_all
		self.companies = companies
		self.keyWords = self.getKeyWords(text_input)
		self.logger = logger

		self.matches = None
		self.getMatches()

	def getKeyWords(self, text_input):
		words = []
		if text_input:
			# Don't remove space from split
			for word in re.split(';|,|\n|\s+',text_input.strip()):
				formattedWord = word.strip().lower().replace("~+~"," ")
				if formattedWord not in words:
					words.append(formattedWord)
		return words

	#Worked method for thread
	def addIfMatch(self,group,company_info):
		company_name = company_info.company_info.name
		ticker = company_info.company_info.ticker
		description = company_info.company_description.description

		company_map = None
		has_matched = False
		if description:
			if self.match_all:
				company_map = {'company_name':company_name,'keyWordMatches':[],
				'description':description, 'company_id':company_info.company_info.uuid, 
				'ipo_date':company_info.ipo_info.date}
				has_matched = True
			else:
				lowerCaseDescription = description.lower()
				for keyWord in self.keyWords:
					if lowerCaseDescription.find(keyWord) > -1:
						if has_matched:
							company_map['keyWordMatches'] = company_map['keyWordMatches'] + [keyWord]
						else:
							company_map = {'company_name':company_name,'keyWordMatches':[keyWord],
							'description':description, 'ipo_date':company_info.ipo_info.date, 'company_id':company_info.company_info.uuid}
							has_matched = True
		if has_matched:
			self.matches[group].append(company_map)
		return


	def getMatches(self):
		#If no keywords and we're not searching for everything, return nothing
		if not (self.keyWords or len(self.keyWords) <= 0) and not self.match_all:
			return None
		else:
			self.matches = {'this_week':[], 'next_week':[], 'future':[], 'past':[]}
			# create pool
			threads = []  
			for row in self.companies:
				group = DateHandling.getGroupFromDate(row.ipo_info.date_week, self.logger)
				if group:
					t = threading.Thread(name='Company Info Fetcher',target=self.addIfMatch,args=(group,row))
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




