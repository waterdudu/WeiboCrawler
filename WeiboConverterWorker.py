'''
Created on 2013-3-25

@author: waterdudu
'''
import threading
import time
import random
from Queue import Queue
import json

from HtmlSaver import HtmlSaver, FavouriteHtmlSaver
import WeiboConverter
from weibo import APIClient

class WeiboConverterWorker(threading.Thread):
	def __init__(self, downloader_pool, threadname, count_in_page, page):
		threading.Thread.__init__(self, name=threadname)
		# pool for image download
		self.downloader_pool = downloader_pool
		self.data          = None
		self.page          = page
		self.count_in_page = count_in_page
		self.client = APIClient(app_key="", app_secret="", redirect_uri="")
		self.json_dir      = "json_dir"
		self.html_dir      = "html_dir"
		self.use_local_file = False

	def run(self):
		########################
		#   run in serial
		########################
		print "requesting data ..."
		self._request_data()
		print "writing json ..."
		self._write_json()
		print "writing html ..."
		self._write_html()
	########################################
	#         json & html dir
	########################################    
	def set_json_dir(self, json_dir):
		self.json_dir = json_dir
	def set_html_dir(self, html_dir):
		self.html_dir = html_dir

	########################################
	#         access token
	########################################    
	def set_access_token(self, access_token):
		self.client.set_access_token(access_token, 1)  # expire_at has no use

	def _get_json_file(self, page):
		filename = "user_page_%d.json" % self.page
		filepath = self.json_dir + "/" + filename
		return filepath
	
	def _read_json_data_from_file(self):
		filepath = self._get_json_file(self.page)
		f = open(filepath, "w")
		c = f.read()
		data = json.loads(c)
		f.close()
	
		return data

	def _request_data(self):
		try:
#			print "requesting status data ..."
			if not self.use_local_file:
				self.data = self.client.statuses.user_timeline.get(count=self.count_in_page, page=self.page)
			else:
				self.data = self._read_json_data_from_file()	
				
		except Exception, e:
			print (e)
			print (self.page)
			raise e
		return

	def _write_json(self):
		#########################################
		#   save to json file
		#########################################
		# TODO:change filename prefix
		filepath = self._get_json_file(self.page)

		f = open(filepath, "w")
		json.dump(self.data, f)
		f.close()
		print "saving %s is done!" % filepath
		return

	def _write_html(self):
		###########################
		#     not use local file
		###########################
		# filename = ""
		# htmlsaver = HtmlSaver(filename=filename)
		filename = "user_page_%d.html" % self.page
		htmlsaver = HtmlSaver(self.downloader_pool, weibo_json=self.data)
		output_file = self.html_dir + "/" + filename 
		htmlsaver.tofile(output_file)
		return

class WeiboFavouriteConverterWorker(WeiboConverterWorker):
	def __init__(self, downloader_pool, threadname, count_in_page, page):
		print "weibo favourite converter worker"
		WeiboConverterWorker.__init__(self, downloader_pool, threadname, count_in_page, page)
		self.set_json_dir("favourite_json_dir")
		self.set_html_dir("favourite_html_dir")

	def _request_data(self):
		try:
			self.data = self.client.favorites.get(count=self.count_in_page, page=self.page)
		except Exception, e:
			print (e)
			print ("page : %d" % self.page)
			raise e
		return

	def _write_html(self):
		###########################
		#     not use local file
		###########################
		# filename = ""
		# htmlsaver = HtmlSaver(filename=filename)
		filename = "user_page_%d.html" % self.page
		htmlsaver = FavouriteHtmlSaver(self.downloader_pool, weibo_json=self.data)
		output_file = self.html_dir + "/" + filename  
		htmlsaver.tofile(output_file)
		return





class WorkerManager(object):
	def __init__(self, number_of_queue):
		self.number_of_queue = number_of_queue
		self.queue = Queue()

	def init_queue(self):
		pass





