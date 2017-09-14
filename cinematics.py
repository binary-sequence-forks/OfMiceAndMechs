cinematicQueue = []
quests = None
main = None
loop = None
callShow_or_exit = None
messages = None

class Cinematic(object):
	def __init__(self,text):
		self.text = text+"\n\n-- press space to proceed -- "
		self.position = 0
		self.endPosition = len(self.text)

	def advance(self):
		if self.position >= self.endPosition:
			return

		main.set_text(self.text[0:self.position])
		if self.text[self.position] in ("\n"):
			loop.set_alarm_in(0.5, callShow_or_exit, '~')
		else:
			loop.set_alarm_in(0.05, callShow_or_exit, '~')
		self.position += 1

def showCinematic(text):
	cinematicQueue.append(Cinematic(text))