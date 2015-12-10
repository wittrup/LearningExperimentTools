#utf-8
#classifier.py
import requests
import urllib
import operator
import os
"""
	A python module for classifying topics in urls using uclassify.com.
	See http://uclassify.com for api-key and documentation
"""

def get_api_key():
	folder = os.path.dirname(__file__)
	with open(os.path.join(folder, 'uclassify.read_api_key.txt')) as api_key_file:
		api_key = api_key_file.read().rstrip()
	return api_key

class Classifier():
	def __init__(self, api_key):
		self.api_key = api_key


	def build_call_url(self, api_url, query_url):
		"Urlencodes the query url and puts it in the api call url"
		return api_url % (self.api_key, urllib.quote_plus(query_url))


	def classify(self, url):
		"""
			calls the api endpoint and returns the json reply
		"""
		r = requests.get( self.build_call_url(self.api_url, url))
		if r:
			json = r.json()
			return json


	def main_topic(self, json):
		"Goes through the list of candidates and returns the one with highest rank/probability"
		candidates = json['cls1']
		return max(candidates.iteritems(), key=operator.itemgetter(1))[0]


########################################################################
#	Topics
########################################################################


class TopicsClassifier(Classifier):
	"""
		Classifying topics. 
	"""
	def __init__(self, api_key):
		Classifier.__init__(self, api_key)
	api_url="https://uclassify.com/browse/uclassify/topics/ClassifyUrl?readkey=%s&output=json&removeHtml=true&version=1.01&url=%s"



"""
	Generating a class for each topic category corresponding to the api's endpoint 
"""
for category in "Art, Busines, Computer, Game, Health, Home, Recreation, Science, Society, Sport".split(", "):
	exec('''class {0}TopicsClassifier(TopicsClassifier):
		"""
			Classifies {0} topics on URL.
		"""
		api_url="https://uclassify.com/browse/uclassify/{1}-topics/ClassifyUrl?readkey=%s&output=json&removeHtml=true&version=1.01&url=%s"
		
		def __init__(self, api_key):
			TopicsClassifier.__init__(self, api_key)
	'''.format(category, category.lower()))


########################################################################
#	Language
########################################################################


class LanguageClassifier(Classifier):
	"""
		Classifies the language of a url
	"""
	def __init__(self, api_key):
		Classifier.__init__(self, api_key)
	api_url="http://uclassify.com/browse/uClassify/Text Language/ClassifyURL?readkey=%s&output=json&removeHtml=true&url=%s&version=1.01"



if __name__ == '__main__':
	api_key = get_api_key()
	classifier = ComputerTopicsClassifier(api_key)
	arts_classifier = ArtTopicsClassifier(api_key)
	
	url = "http://stackoverflow.com/questions/8259001/python-argparse-command-line-flags-without-arguments"
	json = classifier.classify(url)
	print classifier.main_topic(json)
	
	# aRTSY
	url = "http://www.biography.com/people/leonardo-da-vinci-40396"
	print arts_classifier.main_topic(arts_classifier.classify(url))

	#Language
	classifier = LanguageClassifier(api_key)
	url = "http://basicinternet.no"
	json = classifier.classify(url)
	print classifier.main_topic(json)
	
