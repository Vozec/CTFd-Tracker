#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022


import requests,re,json

from utils.logger import logger
from utils.misc   import Create_Rdn_PPL


def isRecaptched(url):
	resp = requests.get(url).text
	if('https://www.google.com/recaptcha/api.js' in resp):
		return True
	return False

def Get_Nonce(url,session):
	res = session.get('%s/login'%url)
	match = re.search('name="nonce"(?:[^<>]+)?value="([0-9a-f]{64})"', res.text)
	if(match):
		return match.group(1)
	return ""

def Register_Random(url):
	user = Create_Rdn_PPL()
	session = requests.session()
	if(Register_Account(session,user,url)):
		Create_Team(session,user,url)
		username,passw = user['pseudo'],user['password']
		logger('Account Created: %s | %s'%(username,passw),'log',0,1)
		return user
	return {'pseudo':'','password':''}

def CheckTeam_User(session,user,url):
	try:
		verif = session.get(url+'/api/v1/users/me').text
		if(type(json.loads(verif)["data"]["team_id"]) == int):
			return True
	except Exception as ex:
		logger("Error to check user account : %s"%str(ex),"error",1,0)
	return False

def CheckUser_Exist(session,user,url):
	try:
		resp = session.get(url+'/users?field=name&q=%s'%user['pseudo']).text.replace("\n","").replace("\t","")
		all_ = list(zip(*list(re.findall(r'<a href="/users/(.*?)">(.*?)</a>',resp))))
		if(len(all_) != 0):
			if(user["pseudo"].lower() in list((map(lambda x: x.lower(), all_[1])))):
				return True  
		return False
	except Exception as ex:
		logger(" [+] Error to check if user exist : %s"%str(ex),"error",1,0)
		return False

def Join_Team(session,user,url):
	try:
		resp = session.post(url+'/teams/join', {
			"name":user["team"],
			"password":user["team_password"],
			"_submit":"Join",
			"nonce":Get_Nonce(url,session)
		}).text
		return CheckTeam_User(session,user,url)
	except Exception as ex:  
		logger(" [+] Error to join the team : %s"%str(ex),"error",1,0)
		return False

def Create_Team(session,user,url):
	try:
		resp = session.post(url+'/teams/new',{
			"name":user["team"],
			"password":user["team_password"],
			"_submit":"Create",
			"nonce":Get_Nonce(url,session)
		}).text
		return CheckTeam_User(session,user,url)
	except Exception as ex:
		logger("Error during team creation : %s"%str(ex),"error",1,0)
		return False

def CheckTeam_Exist(session,user,url):
	try:
		resp = session.get(url+'/teams?field=name&q=%s'%user['team']).text
		all_ = list(zip(*list(re.findall(r'<a href="/teams/(.*?)">(.*?)</a>',resp))))
		if(len(all_) != 0):
			if(user["team"].lower() in list((map(lambda x: x.lower(), all_[1])))):
				return True  
		return False
	except Exception as ex:
		logger(" [+] Error to check if team exist : %s"%str(ex),"error",1,0)
		return False

def Register_Account(session,user,url):
	try:
		rep = session.post('%s/register'%url,{
			"name":user['pseudo'],
			"email":user['email'],
			"password":user['password'],
			"nonce":Get_Nonce(url,session),
			"_submit":"Submit",
			"fields[1]":"y",
			"fields[2]":"y"
		}).text
		return True if('Logout' in rep) else False
	except Exception as ex:
		logger("Error during registration : %s"%str(ex),"error",1,0)
		return False,False

def Login_Account(session,user,url):
	nonce = Get_Nonce(url,session)
	rep = session.post('%s/login'%url,
		data={
			'name': user['pseudo'],
			'password': user['password'],
			'nonce': nonce,
		}
	)
	if('Logout' in rep.text):
		return True
	else:
		return False

def Login_Account_Session(session,token,url):
	session.headers.update({
		"Content-Type": "application/json",
		"Authorization": "Token %s"%config['CTFD_TOKEN']
	})
	resp = json.loads(session.get('%s/api/v1/users/me'%url).text)
	if 'success' in resp and resp['success']:
		return False
	return True


def Auth_CTFd(args,session):    
    if(args.token):
        logger('Trying to connect using Token ...','info',1,0)
        if Login_Account_Session(session,args.token,args.url):
            logger('Session Connected using Token .','log',0,1)
            return session
        else:
            logger('Failed to connect using Token .','info',0,1)

    if(not isRecaptched(args.url)):
        if(args.username and args.password):
            logger('Trying to connect using Creds provided ...','info',1,0)
            user  = {'pseudo':args.username,'password':args.password}
            if(Login_Account(session,user,args.url)):
                logger('Session Connected using Creds provided .','log',0,1)
                return session
            else:
                logger('Failed to connect using Creds provided .','info',0,1)
        else:
            logger('Trying to create a random account ...','info',1,0)
            user = Register_Random(args.url)
            logger('Trying to connect using Creds created ...','info',1,0)
            if(Login_Account(session,user,args.url)):
                logger('Session Connected using Creds created .','log',0,1)
                return session
            else:
                logger('Failed to connect using Creds created .','info',0,1)
            return None
    else:
        logger('Recaptcha Detected !! Please use TOKEN to Login .\n','info',1,0)
        return None
