#!/usr/bin/env python
# -*- coding: utf-8 -*-

DefaultTemplate="twitter_template"
TemplatePath = "resource"

class WeiboTemplate(object):
	def __init__(self, template=DefaultTemplate):
		self.template_path = self._get_template_path(template)
		####################################
		##  template content like a cache
		####################################
		self.template_content = ""

	def set_template(self, template):
		self.template_path= self._get_template_path(template)

	def reset_content(self):
		self.template_content = ""

	def _get_template_path(self, template):
		return TemplatePath + "/" + template + ".weibotemplate"

	def get_template(self):
		if not self.template_content:
			f = open(self.template_path)
			self.template_content = f.read()
			f.close()
		return self.template_content

if __name__ == '__main__':
	pass



