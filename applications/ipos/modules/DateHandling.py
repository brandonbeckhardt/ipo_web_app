from datetime import datetime, timedelta, date, time
import logging

class DateHandling():

	@staticmethod
	def convertRangeToDateTimeExclusiveEndDate(date_range):
		return (datetime(*(date_range[0].timetuple()[:6])),datetime(*((date_range[1]+ timedelta(days=1)).timetuple()[:6])))

	# Gets actual date range for groups  
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
	def getGroupFromDate(dt, logger):
		thisWeekRange = DateHandling.getThisWeekRange()
		nextWeekRange = DateHandling.getNextWeekRange()
		if dt == "future":
			return "future"
		else:
			try:
				dt = datetime.strptime(dt, "%Y-%m-%d").date()
				if dt < thisWeekRange[0]:
					return "past"
				elif dt >= thisWeekRange[0] and dt <= thisWeekRange[1]:
					return "this_week"
				elif dt >= nextWeekRange[0] and dt <= nextWeekRange[1]:
					return "next_week"
				elif dt >= nextWeekRange[0]:
					return "future"
				else:
					logger.info("Unable to find date group for: " + dt)
					return None
			except Exception as e:
				logger.info("Trouble parsing dates")
				logger.info(e)
				return None

	@staticmethod
	def thisWeekOrLater(dt, logger):
		return (DateHandling.getGroupFromDate(dt, logger) in ['this_week', 'next_week', 'future'])

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

	@staticmethod
	def secondsUntilNextDay():
		currentDt = datetime.today() 
		tomorrowDt = datetime(*((date.today() + timedelta(days=1)).timetuple()[:6]))
		difference = tomorrowDt - currentDt
		return timedelta.total_seconds(difference)

	@staticmethod
	def today():
		return datetime.today()

	@staticmethod
	def dateToDatetime(dateInput):
		return datetime.combine(dateInput, time.min)

	@staticmethod
	def dateForDisplay(dateInput):
		return dateInput.strftime("%m/%d/%y")

	@staticmethod
	def dateTimeFormattedForFiles(dateInput):
		return dateInput.strftime("%m-%d-%y_%H-%M")
		

