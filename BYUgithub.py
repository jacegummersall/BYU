#!/usr/bin/python3
#Author: Jace Gummersall

# Save your code (finished or not) into a public github repo.
# Document any assumptions you made, instructions on how to run your code and anything else you want me to know using a README.md file in the root of the directory tree in the repo.
# Reply to this email giving me the link to the repo with your code at or before Wednesday, October 10, 2018. If you don't finish all of the requirements on time please send the link by the deadline anyway.
import os
import json
import requests

def start():
	organization = getOrganization()
	repos = getOrganizationRepos(organization)
	addLicense(organization, repos)

def getOrganization():
	print("What is the name of your organization?")
	organization = input(": ")
	return organization

def getOrganizationRepos(organization):
	# Using the github API, goes through all the public and private github repos in a github organization and checks if they have a license.
	url = 'https://api.github.com/orgs/' + organization + '/repos'
	try:
		response = requests.get(url)
		data = response.json()
		repos = [];
		for i in range(len(data)):
			if data[i]['license'] is None:
				repos.append(data[i]['name'])
		return repos
	except:
		print("Unexpected error:", sys.exc_info()[0])
		raise

def addLicense(organization, repos):
	# Write code that if the license is missing, opens a pull request which adds a license. (More info about licenses can be found here: https://choosealicense.com/)
	for i in range(len(repos)):
		print('Which license would you like to add to ' + repos[i] + '?')
		license = chooseLicense()
		body = getLicenseBody(license)
		text = formatString(body['body'])
		username = input("Username: ")
		pull = {
		  "title": "LICENSE",
		  #"body": text,
		  "head": username + ':master',
		  "base": "master"
		}
		postLicense(organization, username, repos[i], pull)

def getLicenses():
	licenseUrl = 'https://api.github.com/licenses'
	response = requests.get(licenseUrl)
	licenses = response.json()

	return licenses

def chooseLicense():
	licenses = getLicenses()
	names = []
	for i in range(len(licenses)):
		names.append(licenses[i]['name'])

	names.sort()
	for i in range(len(names)):
		print('\t' + str(i + 1) + ') ' + names[i])

	choice = input('Enter the number of the license you would like to add: ')

	url = ''

	for i in range(len(licenses)):
		if licenses[i]['name'] == names[int(choice) - 1]:
			url = licenses[i]['url']

	return url

def getLicenseBody(url):
	licenseUrl = url
	response = requests.get(licenseUrl)
	license = response.json()

	return license

def formatString(text):
	#text = '\"' +  str(text) + '\"'
	#text = text.replace('','')
	return text

def postLicense(organization, user, repo, data):
	url = 'https://api.github.com/repos/' + organization + '/' + repo+ '/pulls'
	os.system('curl --user \"' + user + '\" --data \"' + str(data) + '\" -H \"Content-Type: application/json\" -X POST ' + url)
	#post = requests.post(url, data=json.dumps(text))
	#print(post)

start()



