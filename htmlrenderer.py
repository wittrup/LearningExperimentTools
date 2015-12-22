#coding: utf-8
from jinja2 import Template
import os

def render_to_html(learningpath):
	""" 
		Takes a list of links from the learning path (nodes), and
		renders to html.

		:param learningpath a LearningPath instance 
	"""
	
	#Load template
	folder = os.path.dirname(__file__)
	with open(os.path.join(folder, "learningpath.html")) as htmlfile:
		template = Template(htmlfile.read())
	
	#Render
	return template.render(nodes=learningpath.nodes, title=learningpath.title)


if __name__ == '__main__':
	from model import LearningObject, LearningPath
	import graph

	nodes = graph.fetchInfo([
		"https://msdn.microsoft.com/en-us/library/9fkccyh4.aspx",
		"http://stackoverflow.com/questions/81052/when-should-a-class-member-be-declared-virtual-c-overridable-vb-net",
		"http://www.dotnetperls.com/virtual",
		"http://www.codeproject.com/Articles/816448/Virtual-vs-Override-vs-New-Keyword-in-Csharp"
	])

	# Transforming the list of tuples to a list of LearningObjects
	los = [LearningObject(url=link, title=title) \
				for (label, title, link) in nodes]

	learningpath = LearningPath(nodes=los, title="Testpath")
	print render_to_html(learningpath)
