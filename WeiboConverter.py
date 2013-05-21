#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import logging

logging.basicConfig(level=logging.DEBUG, filename='-----logging-----.txt')
#reload(sys)
#sys.setdefaultencoding('utf-8')

from weibo import APIClient
from WeiboImageDownloader import WeiboImageDownloaderThreadPool,downloader_turple

try:
	import json
except ImportError:
	import simplejson as json

#class HtmlConverter(object):
#	def tweet(self, encoding="utf-8"):
#		r = ''
#		if encoding:
#			r = unicode.encode(r, encoding)

#		return r
# IMAGE_DOWNLOADER_POOL_SIZE = 30
# image_downloader_pool = WeiboImageDownloaderThreadPool(IMAGE_DOWNLOADER_POOL_SIZE)

class StatusHtmlConverter(object):
	'''
	'''
	def __init__(self, downloader_pool, status):
		# json object
		self.downloader_pool   = downloader_pool
		self.status          = self._handle_input(status)
		
		self.profile_image_url = ""
		
		self.reposts_count     = 0
		self.comments_count    = 0
		self.attitudes_count   = 0

		self.original_pic      = ""
		self.thumbnail_pic     = ""
		self.bmiddle_pic       = ""
		# saved two filenames to look up in folder
		self.pic_filename      = ""
		self.retweeted_pic_filename = ""

		self.created_at        = ""
		self.text              = ""

		self.retweeted_status_text            = ""
		self.retweeted_status_domain          = ""
		self.retweeted_status_reposts_count   = ""
		self.retweeted_status_comments_count  = ""
		self.retweeted_status_original_pic    = ""
		self.retweeted_status_bmiddle_pic     = ""
		self.retweeted_status_thumbnail_pic   = ""
		self.retweeted_status_created_at      = ""
		self.retweeted_status_mid             = ""
		self.retweeted_status_attitudes_count = ""

		self._parse()

	def _handle_input(self, status):
		if isinstance(status, str):
			return json.loads(status)
		return status

	def _get_WB_text(self):
		# div
		WB_text_div = '<div class="WB_text">%s</div>'
		return WB_text_div % self.text

	def _get_WB_media_list_thumbnail_file(self):
		return "thumbnail/" + self.pic_filename
	
	def _get_WB_media_expand_media_list_thumbnail_file(self):
		return "thumbnail/" + self.retweeted_pic_filename
	
	def _get_WB_media_list(self):
		if not self.pic_filename: return ""
		# div
		media_filename = "thumbnail/" + self.pic_filename
		WB_media_list = r'''<ul class="WB_media_list">
							<li>
							<div class="chePicMin">
								<img src="%s">
							</div>
							</li>
						</ul>
						''' % media_filename
		return WB_media_list
	
	def _get_WB_media_expand_media_list(self):
		if not self.retweeted_status_original_pic: return ""
		
		r = """<div>
				<ul class="WB_media_list">
					<li>
					<div class="">
						<img style="" src="%s"></img>
					</div>
					</li>
				</ul>
			</div>""" % self._get_WB_media_expand_media_list_thumbnail_file()
		return r
										
	def _get_WB_media_expand(self):
		# div
		WB_media_expand_div = r'''<div class="WB_media_expand">
									<div class="WB_arrow"></div>
									<div>
										<div class="WB_info">%s</div>
										<div class="WB_text">%s</div>
										%s
									</div>
								</div>''' % self._get_WB_media_expand_data()
		return WB_media_expand_div

	def _get_WB_media_expand_data(self):
		return (self.retweeted_status_domain, self.retweeted_status_text, self._get_WB_media_expand_media_list())

	def _get_WB_func(self):
		# TODO:转发，收藏，评论等用链接a，代替plan text
#                            (%d)|转发(%d)|收藏|评论(%d)
		WB_func = '''<div class="WB_func">
						<div class="WB_handle">
							(%d)|转发(%d)|收藏|评论(%d)
						</div>
						<div class="WB_from">
						</div>
					</div>
		''' % self._get_WB_func_handle_data()


		WB_func = WB_func.decode("utf-8")
		return WB_func

	def _get_WB_func_handle_data(self):
#		print (self.attitudes_count, self.reposts_count, self.comments_count)
		return (self.attitudes_count, self.reposts_count, self.comments_count)

	def _image_turple(self):
		return (self.original_pic, self.thumbnail_pic, self.bmiddle_pic)

	def _retweeted_image_turple(self):
		return (self.retweeted_status_original_pic, self.retweeted_status_thumbnail_pic, self.retweeted_status_bmiddle_pic)

	def _can_download_status_images(self):
		return self.original_pic and self.bmiddle_pic and self.thumbnail_pic

	def _can_download_retweeted_images(self):
		return self.retweeted_status_original_pic and self.retweeted_status_thumbnail_pic and self.retweeted_status_bmiddle_pic
	
	def _add_download_task(self):
		if self._can_download_status_images():
#			print "status image download task added"
#			print self._image_turple()
			self.downloader_pool.add_task(downloader_turple, self._image_turple())
		if self._can_download_retweeted_images():
#			print "retweeted image download task added"
			self.downloader_pool.add_task(downloader_turple, self._retweeted_image_turple())

	def _save_pic_filename(self):
		if self.bmiddle_pic:
			self.pic_filename = os.path.basename(self.bmiddle_pic)
		
	def _save_retweeted_pic_filename(self):
		if self.retweeted_status_original_pic:
			self.retweeted_pic_filename = os.path.basename(self.retweeted_status_original_pic)
			
	def _parse(self):
		self.reposts_count  = self._get_status("reposts_count", 0)
		self.comments_count  = self._get_status("comments_count", 0)

		self.original_pic   = self._get_status("original_pic", "")
		self.thumbnail_pic  = self._get_status("thumbnail_pic", "")
		self.bmiddle_pic    = self._get_status("bmiddle_pic", "")
		
		self._save_pic_filename()
		
		self.created_at     = self._get_status("created_at", "")
		self.text           = self._get_status("text", "")
#		print "--- TEXT --- %s" % self.text

#		print self._get_status("user")
		try:
			user_dict = self._get_status("user")
			if user_dict and user_dict.has_key("profile_image_url"):
				self.profile_image_url = user_dict["profile_image_url"]
		except Exception, e:
			print e
			print self.status
			logging.exception("WeiboConverter._parse")
			raise e

		if self.status.has_key("retweeted_status"):
			if self._get_retweeted("user"):
				self.retweeted_status_domain = self._get_retweeted("user")["domain"]
			############################################################################
			#  !!!!      retweeted_status can be deleted     !!!!
			#####################################
			#  "retweeted_status": {
			#    "deleted": "1",
			#    "text": "抱歉，此微博已被作者删除。查看帮助：http://t.cn/zWSudZc",
			#    "created_at": "",
			#    "idstr": "3550665877669686",
			#    "mid": "3550665877669686",
			#    "id": 3550665877669686
			#  },
			############################################################################

			self.retweeted_status_text           = self._get_retweeted("text")
			self.retweeted_status_reposts_count  = self._get_retweeted("reposts_count")
			self.retweeted_status_comments_count = self._get_retweeted("comments_count")

			self.retweeted_status_original_pic    = self._get_retweeted("original_pic")
			self.retweeted_status_bmiddle_pic     = self._get_retweeted("bmiddle_pic")
			self.retweeted_status_thumbnail_pic   = self._get_retweeted("thumbnail_pic")
			self.retweeted_status_created_at      = self._get_retweeted("created_at")
			self.retweeted_status_mid             = self._get_retweeted("mid")
			self.retweeted_status_attitudes_count = self._get_retweeted("attitudes_count")

			self._save_retweeted_pic_filename()
#			print self.status
		#############################################
		#   after parsing, start download task
		#############################################
		#---------------------------------------
		#    image download task
		#---------------------------------------
		self._add_download_task()

		return
	#####################################
	##   get value from status dict
	#####################################
	def _get_status(self, key, value=None):
		if self.status.has_key(key):
			return self.status[key]
		else:
			return value

	#####################################
	##   get value from retweeted dict
	#####################################
	def _get_retweeted(self, key):
		retweeted_status_dict =self.status["retweeted_status"]
		if retweeted_status_dict.has_key(key):
			return retweeted_status_dict[key]
		else:
			return None

	def _get_WB_feed_type_outer_div(self, content):
		r = """<div class="WB_feed_type SW_fun S_line2">
					<div class="WB_feed_detail S_line2">
					%s
					</div>
				</div>""" % content
		return r

	def _get_detail_outer_div(self, content):
		detail_outer_div = """<div class="WB_detail">
								%s
								</div>
						""" % content
		return detail_outer_div


	def tweet(self, encoding="utf-8"):
		'''
		return the html representation of status
		'''
		r = self._get_WB_face()
		r += self._get_WB_detail()
		r = self._get_WB_feed_type_outer_div(r)

		if encoding:
			r = unicode.encode(r, encoding)

		return r
	def _get_WB_face(self):
		WB_face = """<div class="WB_face">
						<a class="WB_face_radius">
							<img width="50px" height="50px" src="%s">
						</a>
					</div>
					""" % self.profile_image_url

		return WB_face

	def _get_WB_detail(self):
		r = ''
		###########################
		#    1) WB_text
		###########################
		r += self._get_WB_text()
		###########################
		#    2) WB_media_list
		###########################
		r += self._get_WB_media_list()
		###########################
		#    3) WB_media_expand
		###########################
		r += self._get_WB_media_expand()
			#~~~~~~~~~~~~
			# WB_arrow
			#~~~~~~~~~~~~
			# div
				# WB_info
				# WB_text
				# WB_media_list div->ul->li->img
		###########################
		#    4) WB_func
		###########################
		try:
			r += self._get_WB_func()
			#~~~~~~~~~~~~
			# WB_handle  (收藏，转发，评论)
			#~~~~~~~~~~~~

			#~~~~~~~~~~~~
			# WB_from
			#~~~~~~~~~~~~
		except:
			print self._get_WB_func_handle_data()

		r = self._get_detail_outer_div(r)

		return r

class FavoriteHtmlConverter(StatusHtmlConverter):
	def __init__(self, downloader_pool,status):
		StatusHtmlConverter.__init__(self, downloader_pool, status)


if __name__ == '__main__':
	s = r'''
	{ "user": {
				"bi_followers_count": 18,
				"domain": "w",
				"avatar_large": "http://tp3.sinaimg.cn/1XXXXXX0/180/4XXXXXXXX2/1",
				"statuses_count": 6450,
				"allow_all_comment": false,
				"id": 1XXXXXX0,
				"city": "1",
				"province": "33",
				"follow_me": false,
				"verified_reason": "",
				"followers_count": 75,
				"location": "浙江 杭州",
				"mbtype": 0,
				"profile_url": "W",
				"block_word": 0,
				"star": 0,
				"description": "W。",
				"friends_count": 566,
				"online_status": 1,
				"mbrank": 0,
				"idstr": "1XXXXXX0",
				"profile_image_url": "http://tp3.sinaimg.cn/1XXXXXX0/50/1XXXXXX0/1",
				"allow_all_act_msg": false,
				"verified": false,
				"geo_enabled": true,
				"screen_name": "W",
				"lang": "zh-cn",
				"weihao": "",
				"remark": "",
				"favourites_count": 1588,
				"name": "W",
				"url": "http://W.wordpress.com",
				"gender": "m",
				"created_at": "Fri Apr 02 07:30:38 +0800 2010",
				"verified_type": -1,
				"following": false
			},
			"reposts_count": 0,
			"favorited": false,
			"retweeted_status": {
				"user": {
					"bi_followers_count": 41,
					"domain": "lejia",
					"avatar_large": "http://tp2.sinaimg.cn/1249193625/180/40017468142/1",
					"statuses_count": 2683,
					"allow_all_comment": true,
					"id": 1249193625,
					"city": "1",
					"province": "31",
					"follow_me": false,
					"verified_reason": "中国性格色彩研究中心创办人， “FPA性格色彩” 创始人",
					"followers_count": 30193596,
					"location": "上海 黄浦区",
					"mbtype": 12,
					"profile_url": "lejia",
					"block_word": 0,
					"star": 0,
					"description": "乐嘉官网 www.lejia.me 性格色彩官网 www.fpaworld.com 工作联系：@米儿小窝fpa",
					"friends_count": 44,
					"online_status": 0,
					"mbrank": 2,
					"idstr": "1249193625",
					"profile_image_url": "http://tp2.sinaimg.cn/1249193625/50/40017468142/1",
					"allow_all_act_msg": false,
					"following": false,
					"verified": true,
					"geo_enabled": false,
					"screen_name": "乐嘉",
					"lang": "zh-cn",
					"weihao": "",
					"remark": "",
					"favourites_count": 1371,
					"name": "乐嘉",
					"url": "http://blog.sina.com.cn/lejia",
					"gender": "m",
					"created_at": "Fri Aug 28 16:14:29 +0800 2009",
					"verified_type": 0,
					"cover_image": "http://ww1.sinaimg.cn/crop.0.3.980.300/4a752e99gw1dzx14dckhaj.jpg"
				},
				"reposts_count": 99,
				"original_pic": "http://ss13.sinaimg.cn/orignal/4a752e994907071875b8c&690",
				"favorited": false,
				"truncated": false,
				"thumbnail_pic": "http://ss13.sinaimg.cn/thumbnail/4a752e994907071875b8c&690",
				"text": "藏族姑娘拿出箱底的两双鞋垫，说我们这穷没啥礼送的，一针一线是自己缝的，您将就着穿吧。我双掌捧着，注视着她们说，这么俊的穿了糟蹋，我要留作女儿的嫁妆，选女婿用",
				"created_at": "Fri Sep 17 16:35:22 +0800 2010",
				"mlevel": 0,
				"idstr": "2710361983",
				"mid": "201100917240337051",
				"visible": {
					"type": 0,
					"list_id": 0
				},
				"attitudes_count": 0,
				"in_reply_to_screen_name": "",
				"source": "<a href=\"http://app.weibo.com/t/feed/9ksdit\" rel=\"nofollow\">iPhone客户端</a>",
				"bmiddle_pic": "http://ss13.sinaimg.cn/bmiddle/4a752e994907071875b8c&690",
				"in_reply_to_status_id": "",
				"comments_count": 360,
				"geo": null,
				"id": 2710361983,
				"in_reply_to_user_id": ""
			},
			"truncated": false,
			"text": "W。",
			"created_at": "Sat Sep 18 00:09:44 +0800 2010",
			"mlevel": 0,
			"idstr": "W",
			"mid": "W",
			"visible": {
				"type": 0,
				"list_id": 0
			},
			"attitudes_count": 0,
			"in_reply_to_screen_name": "",
			"source": "<a href=\"http://weibo.com/\" rel=\"nofollow\">新浪微博</a>",
			"in_reply_to_status_id": "",
			"comments_count": 0,
			"geo": null,
			"id": 2222222222,
			"in_reply_to_user_id": ""
		}
		'''
    
	pool = WeiboImageDownloaderThreadPool(1)
	
	converter = StatusHtmlConverter(pool, s2)
	content = converter.tweet()
	f = open("tweet_from_json.html", "wb")
#	f.write(unicode.encode(content, "utf-8"))
	f.write(content)
#	print (content)
	f.close()
	
	pool.wait_completion()

#####################################################
# save content using unicode.encode(content, 'utf-8')
#####################################################


