# BYU
BYU Script test

Assumptions:
1) Your machine can run python version 3.7 and has the following modules available for import:
      - json
      - requests
      - getpass
      - base64
      - os
2) I assumed that creating a session was preffered for the project rather than using curl commands for everything. 
2) You already have an existing GitHub account
3) Your GitHub account is already a member of an organization on GitHub
4) The repositories in the github organization that you are checking already have a branch created for you to add the license file to and create the pull request from.
5) The branch that you already have created can not already have a file with the same name in it, this program is designed to create a file, not update one.
6) There can not already be a pull request waiting to be open/closed from the branch that you want to create a pull request from.
7) I assumed that the idea was to involve the user so they had a customized experience. The program asks for the login, organization, branch, and type of license for that repository.

In order to run the code: 
1) Copy the "BYUgithub.py" file to your local machine
2) Open terminal or command prompt on your machine, locate the file, and then run 'python3 BYUgithub.py'
3) Follow the onscreen prompts in the program
