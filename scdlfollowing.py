import requests
import json
import subprocess
import argparse

soundcloud_client_ID = '6fc1477cb2e1d7656e735c9792481780'
userLink = ''
removedArtist = ''
artistLinks = []
printList = False

#takes user inputs from commandline and saves them to variables
def parse ():
	global userLink, removedArtist, printList
	#creates the parser with a description
	parser = argparse.ArgumentParser(description='This is a script that gets all tha artists that the user follows and uses the scdc script to download all of their uploads')
	#adds 3 possible arguments
	parser.add_argument('-u', action = "store", dest = 'user', required = True, help = 'The user\'s soundcloud profile link')
	parser.add_argument('-r', action = 'store', dest = 'removed', required = False, help = 'The profile link of the users\' that you don\'t wan\'t to download')
	parser.add_argument('-l', action = 'store_true', dest = 'printList', required = False, help = 'Option to just print out the links of the people the user follows')
	parse = parser.parse_args()
	
	#sets the global variables: userlink and removedArtist
	userLink = parse.user
	removedArtist = parse.removed
	printList = parse.printList

#returns the scoundcloud id based on the soundcloud permalink
def getId (link):
	#data needed to use resolve from the soundcloud api
	resolveUrl = 'http://api.soundcloud.com/resolve'
	resolveParam = dict (
		url = link,
		client_id = soundcloud_client_ID
	)

	#curls the soundcloud api to get the id of soundcloud user with the client api key ;)
	resolve = requests.get(url = resolveUrl, params = resolveParam)

	#converts the response from the get requests into json then sets userId to the value from the 'id' field
	userId = str(resolve.json()['id'])
	return userId

#returns the permalink of all the artist that the user is fillowing
def followings (id):
	#data needed to use /user/followings from the soundcloud api
	followingsUrl = 'http://api.soundcloud.com/users/{0}/followings'.format(id)
	followingsParam = dict (
			client_id = soundcloud_client_ID
	)

	#curls the api to get data about all the channels the user is following
	followings = requests.get(url = followingsUrl, params = followingsParam)

	#converts the output from the api call into json
	data = followings.json()['collection']

	#parses the artist permalink from the json then places it into a list
	links = []
	for artist in data:
		link = artist.get('permalink_url')
		links.append(link)

	return links

#runs the scdl script for every link in the artistLinks list
def download (following):
	#creates a new folder called following
	subprocess.call(["mkdir","following"])

	#for loop going through the list of artists' links
	for artist in following:
		name = artist.replace('https://soundcloud.com/','')
		#creates a folder using the name of the artist
		subprocess.call(['mkdir',"following/"+name])

		#calls the soundcoud downloader script - downloads all the uploads of the artist and places all the music in the created folder
		subprocess.call(['scdl','-t','-c','-l',artist,'--path',"./following/"+name])

#removes matching links from the -r option
def remove (artists):
	global artistLinks
	#cleans then converts the removedArtists input from a string into a list with out spaces
	removed = artists.replace(' ','').replace('https','http').split(',')
	#removes any matches between the removed list and the artistLinks list
	for value in removed:
		artistLinks.remove(value)

#prints out all the links from the artistLinks list
def list ():
	for artist in artistLinks:
		print (artist)

#downloads all the the uploaded songs from every artist in the artistLinks list
def dl ():	
	download(artistLinks)

#takes in command link arguments
parse()
#gets the soundcloud id from the soundcloud user link
scid = getId(userLink)
#gets the links of all the artist the soundcloud user is following
artistLinks = followings(scid)
#removes unwanted artists
if (removedArtist == ''):
	remove(removedArtist)

#checks whether to download or print links
if (printList):
	list()
else:
	dl()
