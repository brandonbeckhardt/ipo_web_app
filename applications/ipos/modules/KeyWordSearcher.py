from Parsers import MarketWatchParser
from Parsers import BloombergParser
import json
# import os
import re


class KeyWordSearcher:
	def __init__(self, text_input,search_future):
		self.search_future = search_future
		self.ipos = MarketWatchParser().ipos
		self.keyWords = self.getKeyWords(text_input)
		self.BloombergParser = BloombergParser()
		self.matches = self.getMatches()

	def getKeyWords(self, text_input):
		words = []
		if text_input:
			for word in re.split(';|,|\n',text_input.strip()):
				formattedWord = word.strip().lower().replace("~+~"," ")
				if formattedWord not in words:
					words.append(formattedWord)
		return words

	def getMatches(self):
		if not self.keyWords or len(self.keyWords) <= 0:
			return None
		else:
			matches = {}
			for group in self.ipos.keys():
				if group == 'this_week' or group =='next_week' or (group=='future' and self.search_future):
					matches[group] = []
					for company_info in self.ipos[group]:
						
						company_name = company_info[0]
						ticker = company_info[1]
						content = self.BloombergParser.getDescription(ticker)
						
						company_map = None
						has_matched = False

						if content:
							description = content.strip().lower()
							for keyWord in self.keyWords:
								if description.find(keyWord) > -1:
									if has_matched:
										company_map['keyWordMatches'] = company_map['keyWordMatches'] + [keyWord]
									else:
										company_map = {'company_name':company_name,'keyWordMatches':[keyWord],'description':description}
										has_matched = True
						if has_matched:
							matches[group].append(company_map)
		return matches

	# def printMatches(self):
	# 	for group in self.matches.keys():
	# 		print group
	# 		print "-------------------------"
	# 		for company in self.matches[group]:
	# 			print company + ": " + str(self.matches[group][company]['keyWordMatches'])
	
	# def outputToFile(self):
	# 	with open('keyWordResults.txt', 'w') as outfile:
	# 		json.dump(self.matches, outfile,indent=4, sort_keys=True)




