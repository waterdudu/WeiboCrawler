#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webbrowser
import json
import os

import time
import threading

import urllib2
from urllib import urlencode
from urllib2 import urlopen, Request

from Queue import Queue

#  http://d36xtkk24g8jdx.cloudfront.net/bluebar/1581971/images/public/paperclip.png

def check_download_path(path):
	if os.path.exists(path) == False:
		os.mkdir(path)

def down_and_save_impl(pic_url, path):
	# TODO: if file exists?
	f = None
	check_download_path(path)
	#####################################
	#      get image filename
	#####################################
	filename = os.path.basename(pic_url)
	filename = path + "/" + filename
	######################
	#   return if exists
	if os.path.exists(filename): 
#		print "existed : %s " % filename
		return
	
	try:
		r = urllib2.Request(pic_url)
#		print "downloading %s " % pic_url
		f = urllib2.urlopen(r, timeout=20)
#		f = urllib2.urlopen(r)
		data = f.read()
	except urllib2.URLError, e:
		print e.reason
		raise e

#	print filename
	with open(filename, "wb") as jpg:
#		print jpg
		print "saving %s " % filename
		jpg.write(data)
		print "saving %s OK" % filename
	if f:
		f.close()
		
def down_and_save(pic_url):
#	print "processing %s" % pic_url
	path = os.path.basename(os.path.dirname(pic_url))
	down_and_save_impl(pic_url, path)
	
def downloader(original_pic_url, thumbnail_pic_url, bmiddle_pic_url):
	down_and_save(original_pic_url)
	down_and_save(thumbnail_pic_url)
	down_and_save(bmiddle_pic_url)

def downloader_turple(t):
	downloader(t[0], t[1], t[2])
	# save image file

class Worker(threading.Thread):
	def __init__(self, tasks):
		threading.Thread.__init__(self)
#		self.urls = urls
		self.tasks = tasks
#		self.daemon = True
		self.setDaemon(True)
		self.start()

	def run(self):
		while True:
			func, args, kargs = self.tasks.get()
			try:
				func(*args, **kargs)
			except Exception, e:
				print e

			self.tasks.task_done()

class WeiboImageDownloaderThreadPool:
	def __init__(self, num_theads):
		self.tasks = Queue(num_theads)
		for t in range(num_theads):
			Worker(self.tasks)

	def add_task(self, func, *args, **kargs):
		self.tasks.put((func, args, kargs))

	def wait_completion(self):
		self.tasks.join()

if __name__ == '__main__':
	o1 = "http://ww4.sinaimg.cn/large/6204ece1jw1dylnkbo8c3j.jpg"
	t1 = "http://ww4.sinaimg.cn/thumbnail/6204ece1jw1dylnkbo8c3j.jpg"
	b1 = "http://ww4.sinaimg.cn/bmiddle/6204ece1jw1dylnkbo8c3j.jpg"
	p1 = (o1, t1, b1)
	o2 = "http://ww4.sinaimg.cn/large/4ba40fc4jw1dzuiax71htj.jpg"
	t2 = "http://ww4.sinaimg.cn/thumbnail/4ba40fc4jw1dzuiax71htj.jpg"
	b2 = "http://ww4.sinaimg.cn/bmiddle/4ba40fc4jw1dzuiax71htj.jpg"
	p2 = (o2, t2, b2)
	# original thumbnail bmiddle
#	downloader(original_pic_url, thumbnail_pic_url, bmiddle_pic_url)
	o3 = "http://ww2.sinaimg.cn/large/642ad0aegw1dziwausrhqj.jpg"
	t3 = "http://ww2.sinaimg.cn/thumbnail/642ad0aegw1dziwausrhqj.jpg"
	b3 = "http://ww2.sinaimg.cn/bmiddle/642ad0aegw1dziwausrhqj.jpg"
	p3 = (o3, t3, b3)
	pool = WeiboImageDownloaderThreadPool(10)
	pool.add_task(downloader_turple, p1)
	pool.add_task(downloader_turple, p2)
	pool.add_task(downloader_turple, p3)
	pool.wait_completion()


"""
	# 1) Init a Thread pool with the desired number of threads
	pool = ThreadPool(200)

	for i, d in enumerate(range(1,50)):
#		print "i : %d, d : %d" % (i, d)
		# 2) Add the task to the queue
		i = i % 10
		pool.add_task(download, urls[i])

	# 3) Wait for completion
	pool.wait_completion()

"""

