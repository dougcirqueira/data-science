"""

This code retrieves data from a Facebook FanPage. This data includes posts and
comments of those retrieved posts.

It is possible to limit the number of posts to be retrieved or comments per posts.
Moreover, it is possible to set the 'since' and 'until' paramenters for retrieving posts.

Always remember to set a valid FanPage name and access token.
All the configs can be set on the config.xml file. For more information, consult this file
and look at the README.md.

@author: Douglas Cirqueira

"""

import urllib
import json
import pandas
import csv
import re
import sys
import os
import time
import xml.etree.ElementTree as ET

reload(sys)
sys.setdefaultencoding("utf8")

def retrieve_posts(fanpage, since, until, oauth_access_token, max_number):
	""" This method retrieves posts on a FanPage and save those in a csv file.
		
		fanpage..............The FanPage name which comments will be retrieved from.
	    since................Since when posts should be retrieved.
	    until................Until when posts should be retrieved.
	    oauth_access_token...Facebook API access token.
	    max_number...........Maximum number of request to retrieve posts. If 0, all posts will be retrieved.
	"""

	if since != None or until != None:
		print 'Since and/or Until present'

		if since == None:
			since = ''

		if until == None:
			until = ''

		"""
		request_url = '''
					 https://graph.facebook.com/v2.0/%s/posts?summary=1&filter=stream&fields=likes.summary(true),comments.summary(true),shares,message,from,type,status_type,picture,link,source,name,caption,description,icon&since=%s&until=%s&limit=100&access_token=%s
				  ''' % (fanpage, since, until, oauth_access_token)
		"""

		request_url = '''
					 https://graph.facebook.com/v2.0/%s/posts?summary=1&filter=stream&fields=likes.summary(true),comments.summary(true),shares,message,from,type,picture,description&until=%s&limit=25&access_token=%s
				  ''' % (fanpage, until, oauth_access_token)


	else:
		print 'No since and until'

		request_url = '''
					 https://graph.facebook.com/v2.6/%s/posts?summary=1&filter=stream&fields=likes.summary(true),comments.summary(true),reactions.type(LOVE).summary(true),shares,message,from,type,picture,description,created_time&limit=25&access_token=%s
				  ''' % (fanpage, oauth_access_token)

		"""
		request_url = '''
					 https://graph.facebook.com/v2.0/%s/posts?summary=1&filter=stream&fields=likes.summary(true),comments.summary(true),shares,message,from,type,picture,description&limit=25&access_token=%s
				  ''' % (fanpage, oauth_access_token)
		"""

		"""
		request_url = '''
					 https://graph.facebook.com/v2.0/%s/posts?summary=1&filter=stream&fields=likes.summary(true),comments.summary(true),shares,message,from,type,status_type,picture,link,source,name,caption,description,icon&limit=100&access_token=%s
				  ''' % (fanpage, oauth_access_token)
		"""
	
	posts_requests_count = 0
	posts_data = []

	data_filename = 'posts_data_%s.csv' % fanpage
	data_type = 'posts'

	variable_names = [
				["Id",
				"Message",
				"Likes",
				"Love",
				"Wow",
				"Haha",
				"Sad",
				"Angry",
				"Comments",
				"Shares",
				"Type",
				"Picture",
				"Description",
				"CreatedTime",
				"Day",
				"Month",
				"Year",
				"Hour",
				"Minute",
				"Seconds"]
			]


	# Save variable names in posts csv file.
	save_variable_names(fanpage, data_filename, variable_names, 'posts')

	# No limit for number of posts
	if max_number == 0:
		while True:
			data = json.load(urllib.urlopen(request_url))

			print data.keys()
			#sys.exit()

			if 'error' in data.keys():
				print 'Error Found'
				print data['error']

				sys.exit()

			try:
				posts_data = data['data']
			except KeyError:
				raise KeyError("Your access_token is probably invalid or has expired.")
			

			parsed_data = parse_posts_with_reactions(posts_data, oauth_access_token)

			save_posts(fanpage, data_filename, parsed_data)

			posts_requests_count += 1

			if (posts_requests_count % 4) == 0:
				print "%d posts retrieved." % (posts_requests_count * 25)

			try:

				request_url = data['paging']['next']

			except KeyError:
				print "End of pages for posts."
				break

	# Retrieve posts until the limit is reached
	else:
		while posts_requests_count < max_number:
			data = json.load(urllib.urlopen(request_url))
			print data.keys()

			if 'error' in data.keys():
				print 'Error Found'
				print data['error']

				sys.exit()

			try:
				posts_data = data['data']
			except KeyError:
				raise KeyError("Your access_token is probably invalid or has expired.")

			parsed_data = parse_posts_with_reactions(posts_data, oauth_access_token)

			save_posts(fanpage, data_filename, parsed_data)

			posts_requests_count += 1

			if (posts_requests_count % 4) == 0:
				print "%d posts retrieved." % (posts_requests_count * 25)

			try:
				request_url = data['paging']['next']

			except KeyError:
				print "End of pages for posts."
				break


def parse_posts(data):
	""" This method parses posts to be saved in a csv file.
		
		data.................Data with posts returned by Facebook API call.

	    Returns:
	      A list of lists with Facebook posts data parsed.
	"""
	parsed_data = []

	for post in data:
		message = unicode(post['message']).encode("utf-8") if "message" in post.keys() else ""
		message = message.replace('\n', ' ').replace('\r', '')

		match = re.match('(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})T(?P<hour>[0-9]{2}):(?P<min>[0-9]{2}):(?P<sec>[0-9]{2})\+0000', post['created_time'])
		datetime = match.groupdict()

		parsed_data.append(
					[post['id'],
					message,
					post['likes']['summary']['total_count'] if 'likes' in post.keys() else 0,
					post['comments']['summary']['total_count'] if 'comments' in post.keys() else 0,
					post['shares']['count'] if 'shares' in post.keys() else 0,
					post['type'] if 'type' in post.keys() else '',
					post['picture'] if 'picture' in post.keys() else '',
					post['description'] if 'description' in post.keys() else '',
					post['created_time'],
					datetime['day'],
					datetime['month'],
					datetime['year'],
					datetime['hour'],
					datetime['min'],
					datetime['sec']]
				)

	return parsed_data


def parse_posts_with_reactions(data, oauth_access_token):
	""" This method parses posts to be saved in a csv file.
		
		data.................Data with posts returned by Facebook API call.

	    Returns:
	      A list of lists with Facebook posts data parsed.
	"""

	parsed_data = []
	# LOVE reactions has been already retrieved.
	reactions = ['WOW', 'HAHA', 'SAD', 'ANGRY']

	for post in data:

		message = unicode(post['message']).encode("utf-8") if "message" in post.keys() else ""
		message = message.replace('\n', ' ').replace('\r', '')

		match = re.match('(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})T(?P<hour>[0-9]{2}):(?P<min>[0-9]{2}):(?P<sec>[0-9]{2})\+0000', post['created_time'])
		datetime = match.groupdict()

		reactions_dict = {}

		# Retrieve Reactions
		for reaction in reactions:
			request_url_reactions = '''
						 https://graph.facebook.com/v2.6/%s?summary=1&fields=reactions.type(%s).summary(true)&access_token=%s
					  ''' % (post['id'], reaction, oauth_access_token)


			data_reactions = json.load(urllib.urlopen(request_url_reactions))




			if 'error' in data_reactions.keys():
				print 'Error Found'
				print data_reactions['error']

				sys.exit()

			try:
				posts_data_reactions = data_reactions['reactions']

				reactions_dict[reaction] = posts_data_reactions['summary']['total_count']
			except KeyError:
				print 'EXCEPTION: NO REACTION %s' % reaction
				reactions_dict[reaction] = 0


		if 'total_count' not in post['comments']['summary'].keys():
			print 'total_count for comments no found.'
			continue

		parsed_data.append(
					[post['id'],
					message,
					post['likes']['summary']['total_count'] if 'likes' in post.keys() else 0,
					post['reactions']['summary']['total_count'] if 'reactions' in post.keys() else 0 , # LOVE reaction
					reactions_dict['WOW'],
					reactions_dict['HAHA'],
					reactions_dict['SAD'],
					reactions_dict['ANGRY'],
					post['comments']['summary']['total_count'] if 'comments' in post.keys() else 0,
					post['shares']['count'] if 'shares' in post.keys() else 0,
					post['type'] if 'type' in post.keys() else '',
					post['picture'] if 'picture' in post.keys() else '',
					post['description'] if 'description' in post.keys() else '',
					post['created_time'],
					datetime['day'],
					datetime['month'],
					datetime['year'],
					datetime['hour'],
					datetime['min'],
					datetime['sec']]
				)

	return parsed_data


def retrieve_comments(fanpage, oauth_access_token, max_number):
	""" This method retrieves comments from all the posts retrieved previously and save those in csv files.
		
		fanpage..............The FanPage name where comments will be retrieved from.
	    oauth_access_token...Facebook API access token.
	    max_number...........Maximum number of requests to retrieve comments. If 0, all comments will be retrieved.
	"""

	posts_df = pandas.read_csv('data/%s/posts/posts_data_%s.csv' % (fanpage, fanpage))

	post_id_list = posts_df['Id']

	total_comments_count = 0

	variable_names = [
				["IdComment",
				"IdPost",
				"Message",
				"Likes",
				"FromName",
				"FromId",
				"CreatedTime",
				"Day",
				"Month",
				"Year",
				"Hour",
				"Minute",
				"Seconds"]
			]

	save_variable_names_sa(fanpage, variable_names)

	# Save variable names in all_comments csv file.
	save_variable_names(fanpage, 'all_comments.csv', variable_names, 'comments')

	for index, post_id in enumerate(post_id_list):

		date = posts_df['CreatedTime'][(posts_df['Id'] == post_id)]

		date = date[index].split('T')[0]

		request_url = '''
						 https://graph.facebook.com/v2.0/%s/comments?&limit=100&access_token=%s
					  ''' % (post_id, oauth_access_token)

		comments_requests_count = 0
		comments_data = []

		data_filename = '%s__%s_comments.csv' % (date, post_id)
		data_type = 'comments'

		# Save variable names in posts csv file.
		save_variable_names(fanpage, data_filename, variable_names, 'comments')

		# No limit for number of posts
		if max_number == 0:
			while True:
				data = json.load(urllib.urlopen(request_url))
				try:
					comments_data = data['data']
				except KeyError:
					raise KeyError("Your access_token is probably invalid or has expired.")

				parsed_data = parse_comments(post_id, comments_data)

				save_comments(fanpage, data_filename, parsed_data)

				save_comments_sa(fanpage, data_filename, parsed_data)

				comments_requests_count += 1
				total_comments_count += len(data['data'])

				if (comments_requests_count % 10) == 0:
					print "%d comments retrieved." % (comments_requests_count * 100)

				try:

					request_url = data['paging']['next']

				except KeyError:
					print "End of pages for comments."
					break

		# Retrieve posts until the limit is reached
		else:
			while comments_requests_count < max_number:
				data = json.load(urllib.urlopen(request_url))
				try:
					comments_data = data['data']
				except KeyError:
					raise KeyError("Your access_token is probably invalid or has expired.")

				parsed_data = parse_comments(post_id, comments_data)

				save_comments(fanpage, data_filename, parsed_data)

				save_comments_sa(fanpage, data_filename, parsed_data)

				comments_requests_count += len(data['data'])
				total_comments_count += len(data['data'])

				if (comments_requests_count % 10) == 0:
					print "%d comments retrieved." % (comments_requests_count * 100)

				try:
					request_url = data['paging']['next']

				except KeyError:
					print "End of pages for comments."
					break

		print "Post %d\tComments Retrieved %d\t ID %s" % (index, (comments_requests_count * 100), post_id)
		print "Total Comments Retrieved %d" % total_comments_count


def parse_comments(post_id, data):
	""" This method parses comments to be saved in a csv file.
		
		post_id..............Post Id of current post to have comments parsed.
		data.................Data with comments returned by Facebook API call.

	    Returns:
	      A list of lists with Facebook comments data parsed.
	"""

	parsed_data = []

	for comment in data:
		message = unicode(comment['message']).encode("utf-8") if "message" in comment.keys() else ""
		message = message.replace('\n', ' ').replace('\r', '')

		match = re.match('(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})T(?P<hour>[0-9]{2}):(?P<min>[0-9]{2}):(?P<sec>[0-9]{2})\+0000', comment['created_time'])
		datetime = match.groupdict()


		parsed_data.append([
					comment['id'],
					post_id,
					message,
					comment['like_count'] if 'like_count' in comment.keys() else 0,
					comment['from']['name'] if 'from' in comment.keys() else '',
					comment['from']['id'] if 'from' in comment.keys() else '',
					comment['created_time'],
					datetime['day'],
					datetime['month'],
					datetime['year'],
					datetime['hour'],
					datetime['min'],
					datetime['sec']
				])

	return parsed_data


def compute_statistics(fanpage):
	""" This method computes some basic statistics about posts retrieved.
		
		fanpage..............The fanpage from which statistics should be computed.
	"""

	data_frame = pandas.read_csv('data/%s/posts/posts_data_%s.csv' % (fanpage, fanpage))

	total = len(data_frame['Likes'])

	mean_likes = (1. * sum(data_frame['Likes'])) / total if sum(data_frame['Likes']) != 0 else 0.0
	mean_comments = (1. * sum(data_frame['Comments'])) / total if sum(data_frame['Comments']) != 0 else 0.0
	mean_shares = (1. * sum(data_frame['Shares'])) / total if sum(data_frame['Shares']) != 0 else 0.0

	print '\n'
	print "Mean of likes for posts on this FanPage: %f" % mean_likes
	print "Mean of comments for posts on this FanPage: %f" % mean_comments
	print "Mean of shares for posts on this FanPage: %f" % mean_shares
	print '\n'

def save_variable_names(fanpage, data_filename, variable_names, data_type):
	""" This method writes variable names in csv files.
		
		fanpage..............The Facebook fanpage.
		data_filename........The name of csv file to be saved.
		variable_names.......Variable names to be saved on the top of a csv file.
		data_type............Type of data, which can be 'posts' or 'comments'
	"""

	if data_type == 'posts':
		path_data = 'data/%s/posts/%s' % (fanpage, data_filename)
	elif data_type == 'comments':
		path_data = 'data/%s/comments/%s' % (fanpage, data_filename)

	if os.path.exists(path_data) == False:
		with open(path_data, 'a') as fp:
			csv_writer = csv.writer(fp, delimiter=',')
			csv_writer.writerows(variable_names)


def save_variable_names_sa(fanpage, variable_names):
	""" This method writes variable names in csv files for sentiment analysis.
		
		fanpage..............The Facebook fanpage.
		variable_names.......Variable names to be saved on the top of a csv file.
	"""

	path_data = 'data/%s/comments/all_comments.csv' % (fanpage)

	with open(path_data, 'w') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		csv_writer.writerows(variable_names)


def save_posts(fanpage, data_filename, data):
	""" This method saves posts in a csv file.
		
		fanpage..............The Facebook fanpage.
		data_filename........The name of csv file to be saved.
		data.................Parsed data to be saved.
	"""

	path = 'data/%s/posts/' % fanpage

	with open(path + data_filename, 'a') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		csv_writer.writerows(data)


def save_comments_sa(fanpage, data_filename, data):
	""" This method saves comments in a csv file for sentiment analysis.
		
		fanpage..............The Facebook fanpage.
		data_filename........The name of csv file to be saved.
		data.................Parsed data to be saved.
	"""
	path = 'data/%s/comments/' % fanpage

	with open(path + '%s_all_comments.csv' % fanpage, 'a') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		csv_writer.writerows(data)


def save_comments(fanpage, data_filename, data):
	""" This method saves comments in a csv file.
		
		fanpage..............The Facebook fanpage.
		data_filename........The name of csv file to be saved.
		data.................Parsed data to be saved.
	"""

	path = 'data/%s/comments/' % fanpage

	with open(path + 'all_comments.csv', 'a') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		csv_writer.writerows(data)

	with open(path + data_filename, 'a') as fp:
		csv_writer = csv.writer(fp, delimiter=',')
		csv_writer.writerows(data)	


def check_paths(fanpage):
	""" This method verifies if all directories necessary to run the code and save data are present.
		Then, if not present, creates directories regarding locations where data must be saved.

		fanpage..............The Facebook fanpage.
	"""

	path_data = 'data'
	path_fanpage = path_data + '/' + fanpage
	path_posts = 'data/%s/posts' % fanpage
	path_comments = 'data/%s/comments' % fanpage

	if os.path.exists(path_data) == False:
		os.mkdir(path_data)

	if os.path.exists(path_fanpage) == False:
		os.mkdir(path_fanpage)	

	if os.path.exists(path_posts) == False:
		os.mkdir(path_posts)

	if os.path.exists(path_comments) == False:
		os.mkdir(path_comments)


class Config(object):
	def __init__(self, fanpage, access_token, posts_quantity, posts_since, posts_until, comments_quantity):

		self.fanpage = fanpage
		self.access_token = access_token

		self.posts_quantity = posts_quantity
		self.posts_since = posts_since
		self.posts_until = posts_until

		self.comments_quantity = comments_quantity


def read_configs():
	""" This method reads all configs from the config.xml file.

	"""

	try:
		tree = ET.parse('config.xml')
	except Exception:
		raise Exception("read_config: Invalid or Nonexistent config.xml file.")
	
	root = tree.getroot()

	try:
		fanpage = root.find('general').find('fanpage').text
		access_token = root.find('general').find('accessToken').text
		posts_quantity = int(root.find('posts').find('quantity').text)
		posts_since = root.find('posts').find('since').text
		posts_until = root.find('posts').find('until').text
		comments_quantity = int(root.find('comments').find('quantity').text)
	except Exception:
		raise Exception("read_config: Invalid config.xml file.")

	if fanpage == None:
		raise Exception("read_config: Invalid value for fanpgage in config.xml file.")

	if access_token == None:
		raise Exception("read_config: Invalid value for access_token in config.xml file.")

	if posts_quantity == None:
		raise Exception("read_config: Invalid value for posts_quantity in config.xml file.")

	if (posts_since != None) and (re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', posts_since) == None):
		raise Exception("read_config: Invalid value for posts_since in config.xml file.")

	if (posts_until != None) and (re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', posts_until) == None):
		raise Exception("read_config: Invalid value for posts_until in config.xml file.")

	if comments_quantity == None:
		raise Exception("read_config: Invalid value for comments_quantity in config.xml file.")

	config = Config(
				fanpage,
				access_token,
				posts_quantity,
				posts_since,
				posts_until,
				comments_quantity
			)

	return config


def main():

	config = read_configs()

	check_paths(config.fanpage)

	retrieve_posts(config.fanpage, config.posts_since, config.posts_until, config.access_token, config.posts_quantity)

	compute_statistics(config.fanpage)

	retrieve_comments(config.fanpage, config.access_token, config.comments_quantity)


if __name__ == '__main__':
	main()
