#!/usr/bin/env python
# -*- coding: utf-8 -*-

from weibo import APIClient
import webbrowser

import threadpool
import os
os.system("mode con cols=300 lines=300")

from WeiboConverterWorker import WeiboConverterWorker, WeiboFavouriteConverterWorker
from WeiboImageDownloader import WeiboImageDownloaderThreadPool

#USE_TOKEN_DIRECTLY = True
USE_TOKEN_DIRECTLY = False

#number_in_one_page = 200            # default number of status in one page
number_in_one_page = 100            # default number of status in one page
# must [1-200]

APP_KEY = '<PUT YOUR APP KEY HERE>' # app key
APP_SECRET = '<PUT YOUR APP SECRET HERE>' # app secret

CALLBACK_URL = 'https://api.weibo.com/oauth2/default.html'# callback url       

class WeiboCrawler(object):
	def __init__(self, app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL):
		#利用官方微博SDK
		self.client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=CALLBACK_URL)
		self.use_token_directly    = False
		self.access_token          = ""
		self.user_set_access_token = ""
		self.expires_in            = 0
		self.use_local_file        = False  # True : use local json file
		self.status_pages          = 2	    # default crawling one page
		self.favorite_pages        = 2      # 
		self.token_file            = "weibo_token"
		
	def crawl(self):
		self._handle_user_input()
		
	def _get_local_token(self):
		if os.path.exists(self.token_file):
			f = open("weibo_token", "r")
			token = f.read()
			return token.strip()	
		else:
			return ""
			
	def _handle_user_input(self):
		self.access_token = self._get_local_token()
		print self.access_token
		if not self.access_token:
			#用得到的url到新浪页面访问
			url = self.client.get_authorize_url()
			webbrowser.open_new(url)

			#手动输入新浪返回的code
			print r"""
	##############################################################
	#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#  To my princess:
	#  without her idea, this could never happen


                              i i'
                              \~;\
                               \; \
                                \ ;\    ====
                                 \ ;\  ==== \
                            __,--';;;\-' (  0
                      __,--';;; ;;; ;;\      >
               __,--'\\ ;;; ;;; ;;; ;;;\--__<
        _ _,--' __,--'\\  ;;; __,~~' \ ;\
       (_)|_,--' __,--'\\;,~~'        \ ;\
       |(_)|_,--'       ~~             \; \
       || |                             \ ;\
        |_/                              !~!,
                                     .---'''---.
                                     |         |
                                     |   xin   |
                                     |         |
                                     `---------'

	#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#  usage:
	#  please copy all characters after code in address bar
	#  https://api.weibo.com/oauth2/default.html?code= 
	#  ie.
	#    code=555168723936b81be030961e31f9c071, then copy 
	#	 555168723936b81be030961e31f9c071
	##########################################################
	If your browser do not open it, open it by copy&paste :
	%s
	##########################################################\n

	#############################################################
	#  please come back quickly, i am waiting for you~~~
	code :""" % url
			code = raw_input()
			if not code:
				print "code must not be empty!"
				return
		
			#新浪返回的token，类似abc123xyz456，每天的token不一样
			r = self.client.request_access_token(code)
			self.access_token = r.access_token
			self._write_token(self.access_token)
			self.expires_in = r.expires_in # token过期的UNIX时间
		else: # user set access token
			self.expires_in   = 1521657821

		#设置得到的access_token
		self.client.set_access_token(self.access_token, self.expires_in)

		#有了access_token后，可以做任何事情了

	def _write_token(self, token):
		f = open(self.token_file, "w")
		f.write(token)
		f.close()
	####################################################################
	#   get uid  XXXXXXXX
	####################################################################
	
	def get_uid(self):
		r = self.client.account.get_uid.get()
		uid = r["uid"]  # type int?
		print "uid : %d" % uid
		return uid
	
	#####################################
	#  get status & favorite count
	#####################################
	def get_status_count(self):
		uids="%d" % self.get_uid()
		r = self.client.users.counts.get(uids=uids)
		d = r[0]
		#----------------------------------------------------------------#
		# fllowers_count : , private_friends_count:, friends_count:, id:
		#----------------------------------------------------------------#
		statuses_count = d["statuses_count"]
		print "statuses_count : %d" % statuses_count
		return statuses_count
	
	####################################
	#   get favirate counts
	####################################
	def get_favorite_count(self):
		r = self.client.users.show.get(uid=self.get_uid())
		print ('getting favourites count...')
		# print (r)
		favourites_count = r["favourites_count"]
		print 'favourites_count : %d' % favourites_count 
		return favourites_count

	def prepared_all_folders(self):
		########################################
		#   mkdir for json file
		########################################
		json_dir = "json_dir"
		if os.path.exists(json_dir) == False:
			os.mkdir(json_dir)
		
		favorite_json_dir = "favourite_json_dir"
		if os.path.exists(favorite_json_dir) == False:
			os.mkdir(favorite_json_dir)
		
		favorite_html_dir = "favourite_html_dir"
		if os.path.exists(favorite_html_dir) == False:
			os.mkdir(favorite_html_dir)
	
		########################################
		#   mkdir for html file
		########################################
		html_dir = "html_dir"
		if os.path.exists(html_dir) == False:
			os.mkdir(html_dir)

	# number_of_pages    = statuses_count / number_in_one_page

	##############################################
	#       debug purpuse 
	##############################################
	#number_of_pages = 2
	#number_in_one_page = 44

	##########  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #############
	####               crawling status                          #####
	##########  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #############
	def crawling_status(self):
		self.status_pages = self.get_status_count() / number_in_one_page
		print ("status pages : %d" % self.status_pages)
		if self.status_pages ==0:
			self.status_pages = 2
		pool = WeiboImageDownloaderThreadPool(4)
		for i in range(1, self.status_pages):
			threadname = "worker %d" % i
			worker = WeiboConverterWorker(pool, threadname, number_in_one_page, i)
			worker.set_access_token(self.access_token)
			worker.use_local_file = self.use_local_file
			#threads.append(worker)
			worker.start()
			worker.join()
		
		pool.wait_completion()

	##########  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #############
	####               crawling favourites                      #####
	##########  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #############
	def crawling_favorite(self):
		self.favorite_pages = self.get_favorite_count() / number_in_one_page
		if self.favorite_pages == 0:
			self.favorite_pages = 2
		pool = WeiboImageDownloaderThreadPool(4)
		for i in range(1, self.favorite_pages):
			threadname = "worker %d" % i
			worker = WeiboFavouriteConverterWorker(pool, threadname, number_in_one_page, i)
			worker.set_access_token(self.access_token)
			worker.use_local_file = self.use_local_file
			
			worker.start()
			worker.join()
			
		pool.wait_completion()

if __name__ == '__main__':
	crawler = WeiboCrawler()
	crawler.crawl()
#	crawler.crawling_favorite()
	crawler.crawling_status()
	pass
