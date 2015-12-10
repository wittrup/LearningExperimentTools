#utf-8
#classifier.py
import requests
import urllib
import operator
import os


def get_api_key():
	folder = os.path.dirname(__file__)
	with open(os.path.join(folder, 'uclassify.read_api_key.txt')) as api_key_file:
		api_key = api_key_file.read().rstrip()
	return api_key

class TopicsClassifier():
	def __init__(self, api_key):
		self.api_key = api_key

	def build_call_url(self, api_url, query_url):
		"Urlencodes the query url and puts it in the api call url"
		return api_url % (self.api_key, urllib.quote_plus(query_url))

	def main_topic(self, json):
		"Goes through the list of candidates and returns the one with highest rank/probability"
		candidates = json['cls1']
		return max(candidates.iteritems(), key=operator.itemgetter(1))[0]

class ComputerTopicsClassifier(TopicsClassifier):
	def __init__(self, api_key):
		TopicsClassifier.__init__(self, api_key)

	api_url="https://uclassify.com/browse/uclassify/computer-topics/ClassifyUrl?readkey=%s&output=json&removeHtml=true&version=1.01&url=%s"

	def classify(self, url):
		r = requests.get( self.build_call_url(self.api_url, url))
		if r:
			json = r.json()
			return json


if __name__ == '__main__':
	api_key = get_api_key()
	classifier = ComputerTopicsClassifier(api_key)

	url = "http://stackoverflow.com/questions/8259001/python-argparse-command-line-flags-without-arguments"

	json = classifier.classify(url)
	print classifier.main_topic(json)

