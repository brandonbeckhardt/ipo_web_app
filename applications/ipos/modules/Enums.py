from enum import Enum
class DataSourceTypes(Enum):
	DATA_MIGRATION = 'DATA_MIGRATION'
	ALL = 'ALL'
	COMPANY = 'COMPANY'
	IPO = 'IPO'
	COMPANY_DESCRIPTION = 'COMPANY_DESCRIPTION'

class DateGroupNames(Enum):
	PAST = 'PAST'
	THIS_WEEK = 'THIS_WEEK'
	NEXT_WEEK = 'NEXT_WEEK'
	FUTURE = 'FUTURE'

class UrlTypes(Enum):
	PUBLIC_COMPANY_URL = {'enum':1, 'table_name':'company_info'}
	PRIVATE_COMPANY_URL = {'enum':2, 'table_name':'ipo_info'}
	BROKER_URL = {'enum':3, 'table_name':'ipo_info'}
	OTHER = {'enum':4, 'table_name':None}