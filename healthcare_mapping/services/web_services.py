from urllib2 import build_opener, Request
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
		request = Request('{0}/{1}?{2}'.format(self.SERVER,path,data))
		return self._connect.open(request)
	
class GoogleMapService(WebService):
	"""
	Talks to the Google Map Web Services
	"""
	SERVER = 'maps.googeapis.com'
	GEOCODE = 'maps/api/geocode/json'
	
	def get_coordinates(self,address):
		data = 'address='+address
		try:
			response = json.loads(self.make_request(self.GEOCODE,data=data).read())
			location = response['results'][0]['geometry']['location']
			return location['lng'],location['lat']
		except IndexError:
			logging.error('No results recieved')
