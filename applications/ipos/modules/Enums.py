from enum import Enum
class DataSourceTypes(Enum):
	DATA_MIGRATION = 'DATA_MIGRATION'
	ALL = 'ALL'
	COMPANY = 'COMPANY'
	IPO = 'IPO'
	COMPANY_DESCRIPTION = 'COMPANY_DESCRIPTION'

class DateGroupNames(Enum):
	PAST = 1
	THIS_WEEK = 2
	NEXT_WEEK = 3
	FUTURE = 4

class UrlTypes(Enum):
	PUBLIC_COMPANY_URL = 1
	PRIVATE_COMPANY_URL = 2
	BROKER_URL = 3
	OTHER = 4