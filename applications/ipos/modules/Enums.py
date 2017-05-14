from enum import Enum
class DataSourceTypes(Enum):
	COMPANY = 1
	IPO = 2
	COMPANY_DESCRIPTION = 3

class DateGroupNames:
	PAST = 1
	THIS_WEEK = 2
	NEXT_WEEK = 3
	FUTURE = 4
