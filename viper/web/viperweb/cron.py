from django_cron import CronJobBase, Schedule

from .parser import Parser


import os
import datetime
import re
import json
import tempfile
import contextlib
import shutil
import requests
from operator import itemgetter

# Logging
import logging

from django.core.files.temp import NamedTemporaryFile

# Viper imports
from viper.common import network
from viper.common.autorun import autorun_module
from viper.common.objects import File
from viper.common.version import __version__
from viper.core.archiver import Extractor
from viper.core.config import __config__
from viper.core.database import Database
from viper.core.plugins import __modules__
from viper.core.project import __project__, get_project_list
from viper.core.session import __sessions__
from viper.core.storage import store_sample, get_sample_path
from viper.core.ui.commands import Commands



def add_file(file_path, name=None, url=None, tags=None, parent=None):
	obj = File(file_path, url)
	new_path = store_sample(obj)
	print(new_path)

	if not name:
		name = os.path.basename(file_path)

	# success = True
	if new_path:
		# Add file to the database.
		db = Database()
		db.add(obj=obj, name=name, tags=tags, url=url, parent_sha=parent)
		# AutoRun Modules
		if cfg.autorun.enabled:
			autorun_module(obj.sha256)
			# Close the open session to keep the session table clean
			__sessions__.close()
		return obj.sha256

	else:
		# ToDo Remove the stored file if we cant write to DB
		return




def open_db(project):
	# Check for valid project
	if project == 'default':
		__project__.open(project)
		return Database()
	else:
		try:
			__project__.open(project)
			return Database()
		except Exception:
			return False

def backup():
	vdb = os.path.join(__project__.base_path, 'viper.db')
	adb = os.path.join(__project__.base_path, 'admin.db')
	ts = datetime.datetime.now()
	ts = __project__.base_path + "/"+ ts.strftime('%Y-%m-%d') + ".bak"
	os.system("sqlite3 {0} .dump > {1}".format(vdb,ts))
	

			
class MyCronJob(CronJobBase):
	RUN_EVERY_MINS = 0 # everyday

	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'viperweb.cron'    # a unique code

	def do(self):
		backup();
		ps = Parser()
		li = ps.list()

		for i in li:
			project = 'default';
			open_db(project)
			url = "http://" + i["url"]
			website = i["url"].split('/')[0]
			tags = i["ip"] + "," + website +"," + website.split('.')[-1]
			downloaded_file = network.download(url, tor=False)
			try:
				if downloaded_file is None:
					continue

				tf = NamedTemporaryFile()
				tf.write(downloaded_file)

				if not tf:
					continue
				tf.flush()
				sha_256 = add_file(tf.name, name=url.split('/')[-1],url=url, tags=tags)
				print("File Added")
			except:
				continue
