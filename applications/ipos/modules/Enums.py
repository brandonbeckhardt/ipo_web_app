from enum import Enum
class DataSourceTypes(Enum):
	ALL = 1
	COMPANY = 2
	IPO = 3
	COMPANY_DESCRIPTION = 4

class DateGroupNames:
	PAST = 1
	THIS_WEEK = 2
	NEXT_WEEK = 3
	FUTURE = 4
