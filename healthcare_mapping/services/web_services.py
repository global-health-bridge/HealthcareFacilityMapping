from urllib2 import build_opener, Request
from urllib import quote
import logging
import json

class WebService(object):
	"""
	Generic Web Service requester
	"""
	SERVER = None
	
	def __init__(self):
		self._connect = build_opener()
	
	def __enter__(self):
		return self
		
	def __exit__(self,type,value,traceback):
		self._connect.close()

	def make_request(self,path,data=None):
		if not self.SERVER:
			raise Exception, 'Server not set.'
		url = '{0}/{1}?{2}'.format(self.SERVER,path,data)
		logging.debug(url)
		return self._connect.open(Request(url),timeout=120)
	
class GoogleMapService(WebService):
	"""
	Talks to the Google Map Web Services
	"""
	SERVER = 'http://maps.googleapis.com'
	GEOCODE = 'maps/api/geocode/json'
	
	def get_coordinates(self,address):
		data = 'address={0}&sensor=false'.format(quote(address))
		try:
			raw_response = self.make_request(self.GEOCODE,data=data).read()
			logging.debug(raw_response)
			response = json.loads(raw_response)
			location = response['results'][0]['geometry']['location']
			return location['lng'],location['lat']
		except IndexError:
			logging.error('No results recieved')
		# except ValueError:
			# logging.error('Request failed')
