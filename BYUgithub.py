#!/usr/bin/python3
#Author: Jace Gummersall

import json
import requests
import getpass
import base64
import os

def start():
	welcome()
	openSession()

def welcome():
	os.system("clear")
	print("###################################################################\n# This program is designed to search an organization on github    #\n# that you are a member of, check to see if the file has a        #\n# license file, and then gives you the option to add a license    #\n# file to each of the repositories that are missing license files #\n###################################################################\n")

def openSession():
	#open session
	s = requests.Session()

	#get user credentials
	print("Please enter your GitHub account credentials\n")
	user = input('Username: ')
	print()
	pswd = getpass.getpass('Password: ')
	
	#login to github
	s.auth = (user, pswd)

	#get organization name
	organization = getOrganization()

	#search for all repos of organization
	orgURL = 'https://api.github.com/orgs/' + organization + '/repos'
	orgRepos = s.get(orgURL)
	orgRepoData = orgRepos.json()

	if str(orgRepos) != '<Response [200]>':
		error = str(orgRepoData)
		print('\n###################################################################\n# There was an error processing your request. Did you spell       #\n# ' + organization + ' correctly?\n# ERROR MESSAGE FROM SERVER:                                      #\n# ' + error + '\n###################################################################\n')
		quit = input("\nTry again (Y) or quit the app (Q)?:")
		s.close()
		if quit[0].upper() == 'Q':
			os.system("clear")
			exit()
		else:
			openSession()
	else:
		repos = []
		
		#filter out repos with licenses so that there are only repos without licenses
		try:
			for i in range(len(orgRepoData)):
				if orgRepoData[i]['license'] is None:
					repos.append(orgRepoData[i]['name'])
		except:
			print('\n###################################################################\n# You have no repositories without a license file in ' + organization + '\n# or your authentication failed. Please try again.                #\n###################################################################\n')
			quit = input("\nTry again (Y) or quit the app (Q)?:")
			s.close()
			if quit[0].upper() == 'Q':
				os.system("clear")
				exit()
			else:
				openSession()

		#display repos missing licenses
		displayRepos(repos)

		#get info for file creation
		info = {
			'same':'N'
		}

		#filter through each repo to create the license file and pull request
		result = []
		for i in range(len(repos)):
			#check if info needs to be updated
			if info['same'] == "N":
				info = getInfo()
			info['branch'] = getBranch(repos[i])
			#create a the license file
			fileObj = fileCreation(s, organization, repos[i], info)
			#create pull request
			createPullRequest(s, info, organization, repos[i])
			outcome = {
				'repo':repos[i],
				'name':info['name'],
				'license': resultBody.strip()
			}
			result.append(outcome)
								
		s.close()
		complete(result)

def getOrganization():
	print("\n###################################################################\n# What is the name of the GitHub organization you want to search  #\n# through the repositories that are missing a license file        #\n###################################################################\n")     
	organization = input("Organization: ")
	return organization

def displayRepos(repos):
	print("\n###################################################################\n# Below is a list of the all of the repositoris that are missing  #\n# a license file.                                                 #\n###################################################################\n")
	try:
		for i in range(len(repos)):
			print('\t' + str(i + 1) + ') ' + repos[i])
	except:
		print('\n###################################################################\n# You have no repositories without a license file in ' + organization + '\n###################################################################\n')
		s.close()

def getInfo():
	print("\n###################################################################\n# Please provide your name, email and name of an ALREADY EXISTING #\n# BRANCH to add it to, in order to create the license file        #\n###################################################################\n") 
	name = input("Name: ")
	email = input("Email: ")
	same = input("Will you use this same information for all the licenses you will be adding?(Y/N):")
	info = {
		"name" : name,
		"email": email,
		"same": same[0].upper()
	}
	return info

def getBranch(repo):
	print('\n###################################################################\n# Which branch would you like to add the license to in ' + repo + '?\n# NOTE: the branch must already exist in GitHub                   #\n###################################################################\n')
	branch = input("Branch (must already exist): ")

	return branch

def fileCreation(s, organization, repo, info):
	filename = input("\nFile name (cannot be the same name as somethign already in your repository. \'LICENSE.md\' is the reccomended name for a license):")
	print()
	fileURL = 'https://api.github.com/repos/' + organization + '/' + repo + '/contents/' + filename
	filePayload = createFile(organization, repo, info)
	file = s.put(fileURL, json=filePayload)
	if str(file) != '<Response [201]>':
		error = file.json()
		error = error['message']
		print('\n###################################################################\n# ERROR FROM SERVER:                                              #\n# ' + error + '\n###################################################################\n')
		quit = input("\nTry again (T), Skip (S) or quit the app (Q)?:")
		if quit[0].upper() == 'Q':
			os.system("clear")
			exit()
		elif quit[0].upper() == 'T':
			fileCreation(s, organization, repo, info)
	return filePayload

def createFile(organization, repo, info):
	text = addLicense(organization, repo)
	byte_string = text.encode('utf-8')
	content = base64.b64encode(byte_string)
	file = {
		"message": "Add license file",
		"committer": {
		"name": info['name'],
		"email": info['email']
	},
		"content": content.decode('utf-8'),
		"branch": info['branch']
	}
	return file

def addLicense(organization, repo):
	print('\n###################################################################\n# Which license would you like to add to ' + repo + '?\n###################################################################\n')
	license = chooseLicense()
	body = getLicenseBody(license)

	return body['body']

def chooseLicense():
	licenses = getLicenses()
	names = []
	for i in range(len(licenses)):
		names.append(licenses[i]['name'])

	names.sort()
	for i in range(len(names)):
		print('\t' + str(i + 1) + ') ' + names[i])

	print()
	choice = input('Enter the number of the license you would like to add: ')

	url = ''

	for i in range(len(licenses)):
		if licenses[i]['name'] == names[int(choice) - 1]:
			url = licenses[i]['url']
			global resultBody 
			resultBody= licenses[i]['name']

	return url

def getLicenses():
	licenseUrl = 'https://api.github.com/licenses'
	response = requests.get(licenseUrl)
	licenses = response.json()

	return licenses

def getLicenseBody(url):
	licenseUrl = url
	response = requests.get(licenseUrl)
	license = response.json()

	return license

def createPullRequest(s, info, organization, repo):
	pullPayload = pullRequest(info)
	pullRequestUrl = 'https://api.github.com/repos/' + organization + '/' + repo + '/pulls'
	pull = s.post(pullRequestUrl, json=pullPayload)
	if str(pull) != '<Response [201]>':
		error = pull.json()
		error = error['message']
		print('\n###################################################################\n# ERROR FROM SERVER:                                              #\n# ' + error + '\n###################################################################\n')
		quit = input("\nTry again (T), Skip (S) or quit the app (Q)?:")
		if quit[0].upper() == 'Q':
			os.system("clear")
			exit()
		elif quit[0].upper() == 'T':
			createPullRequest(s,info, organization, repo)

def pullRequest(info):
	pull = {
	  'title': 'LICENSE',
	  'head': info['branch'],
	  'base': 'master'
	}
	return pull

def complete(result):
	os.system("clear")
	for i in range(len(result)):
		print(str(result[i]['name']) + ' added ' + str(result[i]['license']) + ' to ' + str(result[i]['repo'] + ' repository'))
	exit()

start()
