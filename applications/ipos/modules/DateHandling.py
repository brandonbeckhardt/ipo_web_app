from datetime import datetime, timedelta, date

class DateHandling():

	@staticmethod
	def convertRangeToDateTimeExclusiveEndDate(date_range):
		return (datetime(*(date_range[0].timetuple()[:6])),datetime(*((date_range[1]+ timedelta(days=1)).timetuple()[:6])))

	@staticmethod
	def getDateWeekFromGroup(group):
		if group == "future":
			return "future"
		elif group == "this_week":
			return str(DateHandling.getThisWeekRange()[0])
		elif group == "next_week":
			return str(DateHandling.getNextWeekRange()[0])
		return None

	@staticmethod
	def getGroupFromDate(date):
		thisWeekRange = DateHandling.getThisWeekRange()
		nextWeekRange = DateHandling.getNextWeekRange()
		if date == "future":
			return "future"
		else:
			date = datetime.strptime(date, "%Y-%m-%d").date()
			if date < thisWeekRange[0]:
				return "past"
			elif date >= thisWeekRange[0] and date <= thisWeekRange[1]:
				return "this_week"
			elif date >= nextWeekRange[0] and date <= nextWeekRange[1]:
				return "next_week"
			else:
				return "future"

	@staticmethod
	def getThisWeekRange():
		dt = date.today()
		daysFromMonday = timedelta(days=dt.weekday())
		start = dt - daysFromMonday
		end = start + timedelta(days=6)
		return (start,end)

	@staticmethod
	def getNextWeekRange():
		dt = date.today()
		daysFromMonday = timedelta(days=dt.weekday())
		start = dt - daysFromMonday + timedelta(days=7)
		end = start + timedelta(days=6)
		return (start,end)