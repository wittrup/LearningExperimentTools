#!/usr/bin/env python
#coding: utf-8
import graphviz
import re
import requests
import requests_cache
from bs4 import BeautifulSoup
import sys
import argparse
import classification
from model import LearningPath, LearningObject
import htmlrenderer
import os
import webbrowser
try:
	#py 3.x
	from urllib.parse import urlparse
except:
	#py 2.x
	from urlparse import urlparse

attendees = {}
globallabels = {}
VIEW_OUTPUT_SETTING = True
OUTPUT_FOLDER = ""
# Builds a topic classifier
api_key = classification.get_api_key()
# Make it
classifier = classification.ComputerTopicsClassifier(api_key)

def fetchLinks(iterable):
	vask = lambda x: re.search(r"http[^\s]+", x).group(0).rstrip()
	return [vask(line) for line in iterable if "http" in line]


def guid(link):
	global globallabels
	if link not in globallabels:
		globallabels[link] = str(len(globallabels)+1)
	return globallabels[link]

def load_text(text):
	attendees = {}
	for attendee in text.split('##')[1:]:
			lines = attendee.split("\n")
			name = lines[0].rstrip()
			links = fetchLinks(lines)
			attendees[name] = links
	return attendees


def load_file(filename):
	attendees = {}
	# Henter ut urler fra tekstfilen
	with open(filename) as datafile:
		attendees = load_text(datafile.read())
	return attendees


class LinkMeta():
	def  __init__(self, link):
		self.link = link
		self.urlparts = urlparse(link)


	def parse(self):
		""" Extracting intels about ze link for you sir. """
		self.label = guid(self.link)
		
		r = requests.get(self.link)
		if r:
			soup = BeautifulSoup(r.text, 'html.parser')
			try:
				self.title = soup.select("title")[0].string

				self.meta = fetchMeta(soup)
				#print meta
			except:
				self.title=""
		else:
			self.title=""

		self.classify()
		return self


	def classify(self):
		#CLASSIFY
		self.json = classifier.classify(self.link)
		self.main_topic = classifier.main_topic(self.json)


	def domain(self):
		return self.urlparts.netloc.split(":")[0]

	#should be __str__ maybe, but I find it clumsy to type str(around everything).
	def __repr__(self):
		""" Defaults to textual representation """
		return self.textual_representation()

	def textual_representation(self):
		if self.urlparts.fragment is not "":
			return "[%d]%s - %s\n%s" % (self.label, self.title, self.urlparts.fragment, self.domain())
		else:
			return "[%d]%s\n%s" % (self.label, self.title,  self.domain())


def fetchInfo(links):
	# Genererer unike labler:
	# Henter linken og forsøker hente tittelen
	labels = {}
	nodes = []
	for link in links:
		if link not in labels:
			meta = LinkMeta(link).parse()
			
			#title += "{%s}" % main_topic
			print(meta.main_topic)
			labels[link] = (meta.label, meta)
			nodes.append(meta)
	return nodes



def fetchMeta(soup):
	"Fetches metainfo from a html soup"
	return soup.findAll(attrs={"name":"description"}) + soup.findAll(attrs={"name":"keyword"})

def makeGraph(name, nodes):
	dot = graphviz.Digraph(comment='Learning Path %s' %name)
	# Build the graph
	
	for i, nodeinfo in enumerate(nodes):
		label, title, link = nodeinfo.label, nodeinfo.title, nodeinfo.link
		fragment = nodeinfo.urlparts.fragment
		domain = nodeinfo.domain()

		print(domain)
		nodetext =  "[%s] %s-%s\n%s" % (label, title, fragment, domain )
		dot.node(label, nodetext)
		if i < len(nodes)-1:
			#next node
			next_node = nodes[i+1]
			dot.edge(label, next_node.label)
	return dot


def nodeinfos_to_LearningPath(nodes, name=""):
	los = [LearningObject(url=m.link, title=m.title) \
				for m in nodes]
	return LearningPath(los, title=name)


def draw_learning_paths(attendees):
	all_nodes = []
	# Making learning paths
	for name, links in attendees.items():
		nodes = fetchInfo(links)
		all_nodes.append(nodes)

		# Make dot file + pdf
		g = makeGraph(name, nodes)
		g.render(name, view=VIEW_OUTPUT_SETTING, directory=OUTPUT_FOLDER)
		
		# Make html
		learningpath = nodeinfos_to_LearningPath(nodes, name)
		
		hfname="%s.html"%name
		with open(hfname, "w+") as htmlfile:
			htmlfile.write(
				htmlrenderer.render_to_html(learningpath).encode('utf-8')
			)
			if VIEW_OUTPUT_SETTING:
				webbrowser.open(hfname)
	return all_nodes


def draw_agregated_graph(all_nodes, name):
	# Making agregated graph
	G = graphviz.Digraph(comment='%s - %s' % (name, "Agregated Graph"))
	for nodes in all_nodes:
		for i, node in enumerate(nodes):
			label, title, link = node.label, node.title, node.link
			G.node(label, label)
			#next node
			if i < len(nodes)-1:
				#next node
				next_node = nodes[i+1]
				G.edge(label, next_node.label)

	G.render("%s-Agregated_Graph"%(name), directory=OUTPUT_FOLDER, view=VIEW_OUTPUT_SETTING)


def make_graphs(filename):

	attendees = load_file(filename)
	# One side effect not enough? How about two for you!
	all_nodes = draw_learning_paths(attendees)
	draw_agregated_graph(all_nodes, filename)


def init(filename):
	requests_cache.install_cache(filename)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Make Learning Path Graphs.')
	
	parser.add_argument(
		'files', nargs='+',
				 help="The file(s) to process")
	parser.add_argument(
		'--folder', 
				help='Set output folder for generated graphviz files',
				default='')
	parser.add_argument(
		'--view', action="store_true", 
				help='If provided, the generated pdfs will be displayed')
	# Get the arguments
	args = parser.parse_args()
	VIEW_OUTPUT_SETTING = args.view
	OUTPUT_FOLDER = args.folder
	
	print ("Building graphs")
	print ("Arguments given:")
	print(args)

	# Cache it.
	for filename in args.files:
		# Lets not waste bandwith, cache all web requests.
		requests_cache.install_cache(filename)
		
		make_graphs(filename)
	