#!/usr/bin/env python
#coding: utf-8
import graphviz
import re
import requests
import requests_cache
from bs4 import BeautifulSoup
import sys
import argparse

attendees = {}
globallabels = {}
VIEW_OUTPUT_SETTING = True
OUTPUT_FOLDER = ""

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
	for attendee in text.split('#')[1:]:
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



def fetchInfo(links):
	# Genererer unike labler:
	# Henter linken og forsøker hente tittelen
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
					meta = fetchMeta(soup)
					#print meta
				except:
					title=""
			else:
				title=""
			labels[link] = (label, title)
			nodes.append((label, title, link))
	return nodes



def fetchMeta(soup):
	"Fetches metainfo from a html soup"
	return soup.findAll(attrs={"name":"description"}) + soup.findAll(attrs={"name":"keyword"})

def makeGraph(name, nodes):
	dot = graphviz.Digraph(comment='Learning Path %s' %name)
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

def draw_learning_paths(attendees):
	all_nodes = []
	# Making learning paths
	for name, links in attendees.items():
		nodes = fetchInfo(links)
		all_nodes.append(nodes)
		fn = u"%s" % name
		g = makeGraph(name, nodes)
		g.render(name, view=VIEW_OUTPUT_SETTING, directory=OUTPUT_FOLDER)
	return all_nodes


def draw_agregated_graph(all_nodes, name):
	# Making agregated graph
	G = graphviz.Digraph(comment='%s - %s' % (name, "Agregated Graph"))
	for nodes in all_nodes:
		for i, node in enumerate(nodes):
			label, title, link = node
			G.node(label, label)
			#next node
			if i < len(nodes)-1:
				#next node
				next_label, next_title, next_link = nodes[i+1]
				G.edge(label, next_label)

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
		'--silent', action="store_true", 
				help='If provided, the generated pdfs will not be displayed (default behavior)')
	# Get the arguments
	args = parser.parse_args()
	VIEW_OUTPUT_SETTING = args.silent
	OUTPUT_FOLDER = args.folder
	

	# Cache it.
	for filename in args.files:
		# Lets not waste bandwith, cache all web requests.
		requests_cache.install_cache(filename)
		
		make_graphs(filename)
	