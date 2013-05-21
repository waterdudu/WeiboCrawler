#!/usr/bin/env python
# -*- coding: utf-8 -*-

from WeiboConverter import StatusHtmlConverter,FavoriteHtmlConverter
from WeiboTemplate import WeiboTemplate
try:
	import json
except ImportError:
	import simplejson as json


class HtmlSaver(object):
	def __init__(self,downloader_pool, weibo_json=None, filename=None):
		self.downloader_pool = downloader_pool
		self.content  = ""
		self.statuses = None
		self.template = WeiboTemplate()
		if filename:
			self.json_filename = filename
		else:
			if isinstance(weibo_json,dict) == False:
				raise Exception("weibo_json must be an dictionary!")
			self.statuses = weibo_json["statuses"]
		return

	def _tohtml(self):
		#############################
		#      read from file
		#############################
		if self.statuses == None:
			f = open(self.json_filename)
			c = f.read()
			f.close()
			j = json.loads(c)
			self.statuses = j["statuses"]

		# print "total %d weibo status" % len(self.statuses)

		for status in self.statuses:
			converter = StatusHtmlConverter(self.downloader_pool, status)
			weibo_content = converter.tweet("utf-8")
			self.content += weibo_content
		# print self.content
		return self.content

	def tofile(self, filename):
		###############################
		#    convert json to html
		###############################
		self._tohtml()
		template = self.template.get_template()
		content = template % self.content
		f = open(filename, "w")
		f.write(content)
		f.close()

class FavouriteHtmlSaver(HtmlSaver):
	def __init__(self, downloader_pool, weibo_json=None, filename=None):
#		HtmlSaver.__init__(self, downloader_pool, weibo_json, filename)
		self.downloader_pool = downloader_pool
		self.content  = ""
		self.statuses = None
		self.template = WeiboTemplate()
		if filename:
			self.json_filename = filename
		else:
			if isinstance(weibo_json,dict) == False:
				raise Exception("weibo_json must be an dictionary!")
			self.statuses = weibo_json["favorites"]
		return

	def _tohtml(self):
		#############################
		#      read from file
		#############################
		if self.statuses == None:
			f = open(self.json_filename)
			c = f.read()
			f.close()
			j = json.loads(c)
			self.statuses = j["favorites"]

		# print "total %d weibo status" % len(self.statuses)

		for favorite_element in self.statuses:
			##########################################################
			#   favorite dic is different from status dict
			# status = [{'status' : {'user':{}, 'text':'', ..}}, {}, {}]
			#   passing 
			##########################################################
			#
#			print '-' * 20
#			print favorite_element
#			print 'x' * 20
			status = favorite_element["status"]
#			print status
			converter = FavoriteHtmlConverter(self.downloader_pool, status)
			weibo_content = converter.tweet("utf-8")
			self.content += weibo_content
		# print self.content
		return self.content



if __name__ == '__main__':
	filename = "testdata/user_page_1.json"
	htmlsaver = HtmlSaver(filename=filename)
	htmlsaver.tofile("testdata/user_page_1.html")


