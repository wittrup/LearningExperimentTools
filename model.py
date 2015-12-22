class LearningObject():
	# has url, title
	def __init__(self, url=None, title=None):
		self.url = url
		self.title = title

	
class LearningPath():
	# has learning object, in order
	def __init__(self, nodes=None, title=None):
		self.nodes = [] if nodes is None else nodes
		self.title = title