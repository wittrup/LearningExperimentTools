#coding: utf-8
import graphviz
import re
import requests
from bs4 import BeautifulSoup



def fetchLinks(iterable):
	vask = lambda x: re.search(r"http[^\s]+", x).group(0).rstrip()
	return [vask(line) for line in iterable if "http" in line]

# Henter ut urler fra tekstfilen
attendees = {}
with open('virtual members C#.txt') as datafile:
	for attendee in datafile.read().split('#')[1:]:
		lines = attendee.split("\n")
		name = lines[0].rstrip()
		print name
		links = fetchLinks(lines)
		print links
		attendees[name] = links

globallabels = {}
def guid(link):
	global globallabels
	if link not in globallabels:
		globallabels[link] = str(len(globallabels)+1)
	return globallabels[link]


def fetchInfo(links):
	# Genererer unike labler:
	labels = {}
	nodes = []
	for link in links:
		if link not in labels:
			label = guid(link)
			r = requests.get(link)
			if r:
				soup = BeautifulSoup(r.text, 'html.parser')
				try:
					title = soup.select("title")[0].string
				except:
					title=""
			else:
				title=""
			labels[link] = (label, title)
			nodes.append((label, title, link))
	return nodes


def makeGraph(name, nodes):
	dot = graphviz.Digraph(comment='Learning Experiment, virtual members C# - %s' %name)
	# Build the graph
	
	for i, nodeinfo in enumerate(nodes):
		label, title, link = nodeinfo
		domain = link.split("/")[2]
		print domain
		nodetext =  "[%s] %s\n%s" % (label, title, domain)
		dot.node(label, nodetext)
		if i < len(nodes)-1:
			#next node
			next_label, next_title, next_link = nodes[i+1]
			dot.edge(label, next_label)
	return dot


all_nodes = []
# Making learning paths
for name, links in attendees.items():
	nodes = fetchInfo(links)
	all_nodes.append(nodes)
	fn = u"%s" % name
	print fn
	g = makeGraph(name, nodes)
	g.render(name, view=True)


# Making agregated graph
G = graphviz.Digraph(comment='Learning Experiment, virtual members C# - %s' % "Agregated Graph")
for nodes in all_nodes:
	for i, node in enumerate(nodes):
		label, title, link = node
		G.node(label, label)
		#next node
		if i < len(nodes)-1:
			#next node
			next_label, next_title, next_link = nodes[i+1]
			G.edge(label, next_label)

G.render("Agregated Graph", view=True)
