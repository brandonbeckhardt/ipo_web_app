import json
# import os
import re
import threading
import time


class DataMatcher:
	def __init__(self, text_input,search_future,match_all,companies):
		self.search_future = search_future
		self.match_all=match_all
		self.companies = companies
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
	def addIfMatch(self,group,company_info):
		company_name = company_info["company_name"]
		ticker = company_info["ticker"]
		description = company_info["description"]
		
		company_map = None
		has_matched = False
		if description:
			if self.match_all:
				company_map = {'company_name':company_name,'keyWordMatches':[],'description':description}
				has_matched = True
			else:
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
		if not (self.keyWords or len(self.keyWords) <= 0) and not self.match_all:
			return None
		else:
			self.matches = {}
			for group in self.companies.keys():
				if group == 'this_week' or group =='next_week' or (group=='future' and self.search_future):
					self.matches[group] = []
					# create pool					    
					threads = []  
					for idx, company_info in enumerate(self.companies[group]):
						t = threading.Thread(name='Company Info Fetcher',target=self.addIfMatch,args=(group,company_info))
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



