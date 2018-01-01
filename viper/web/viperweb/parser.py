import BeautifulSoup as bs
import requests
import sys
import feedparser
import urllib2
import re
import unicodedata
import json


class Parser:
	def parse(self,url):
		# Returns the html code
		headers = {
	    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}
		r = requests.get(url, headers=headers, timeout=5)
		return r.text

	def malwaredl(self,xml):
		print ("- Fetching from Malware Domain List")
		mdl=[]
		soup = bs.BeautifulSoup(xml)
		for row in soup('description'):
			mdl.append(row)
		del mdl[0]
		mdl_data=[]
		for row in mdl:
			text = row.getText()
			# Convert to string
			text = unicodedata.normalize('NFKD', text).encode('ascii','ignore')
			text = text.replace('IP address', 'ip')
			text = text.replace('Host', 'url')
			li = text.split(',')

			# Convert to dictionary
			d = dict([map(str.strip,i.split(':')) for i in li])
			for key,value in d.iteritems():
				d[key] = str(value)
			mdl_data.append(d)

		print ("-- Found %s urls" % len(mdl))
		return mdl_data

	def vxvault(self,xml):
		print ("- Fetching from VXVault")
		vxv=[]
		soup = bs.BeautifulSoup(xml)
		table = soup.find('table')
		for tr in table('tr'):
			li = []
			ki = ["date", "url", "md5", "ip", "tool"]
			i = 0;
			vi = {}
			for td in tr('td'):
				data = td.getText()
				data = unicodedata.normalize('NFKD', data).encode('ascii','ignore')
				data = data.replace('&nbsp;','')
				data = data.replace('[D]','')
				vi[ki[i]] = data
				i = i + 1
			vi.pop("date", None);
			vi.pop("tool", None);
			vxv.append(vi)

		del vxv[0]
		print ("-- Found %s urls" % len(vxv))
		return vxv

	def list(self):
		vx = "http://vxvault.net/ViriList.php"
		mdl = "https://www.malwaredomainlist.com/hostslist/mdl.xml"
		#murl = "http://malwareurls.joxeankoret.com/normal.txt"
		vlist = self.vxvault(self.parse(vx))
		mlist = self.malwaredl(self.parse(mdl))
		return vlist + mlist;