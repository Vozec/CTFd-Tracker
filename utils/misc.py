#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

from requests.compat import urlparse
import requests,datetime,names,random,re
from rich import progress

from utils.logger import *

def header():
    ## header
    logger(r"""
   ___  _____  ___   _   _____                _    
  / __\/__   \/ __\_| | /__   \_ __ __ _  ___| | _____ _ __ 
 / /     / /\/ _\/ _` |   / /\/ '__/ _` |/ __| |/ / _ \ '__|
/ /___  / / / / | (_| |  / /  | | | (_| | (__|   <  __/ |   
\____/  \/  \/   \__,_|  \/   |_|  \__,_|\___|_|\_\___|_|                                                

""",'warning',0,0)


def Cleaner_url(url):
    return 'https://%s'%urlparse(url.rstrip('/')).hostname

def Check_Ctfd(url):
    try:
        res = requests.get(url).text
        if('Powered by CTFd' in res or 'We are checking your browser' in res):
            return True
    except Exception as ex:
        logger('Error during ctfd check : %s'%str(ex),"error",1,0)
    return False

def Resolve_CTF(url):
    return ' '.join(urlparse(url).hostname.split('.')[:-1])

def Resolve_user(id_user,users):
    return [name for name,data in users.items() if data['id'] == id_user][0]

def Convert2Timestamp(time):
    return round(datetime.strptime(time, '20%y-%m-%dT%H:%M:%S+00:00').timestamp())

def Create_Rdn_PPL():
    pseudo = names.get_last_name()+str(random.randint(1,99))
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-*:/;."
    user = {
        "pseudo":pseudo,
        "email":pseudo+'@tempr.email',
        "password":''.join(random.choice(charset) for i in range(12)),
        "team":pseudo+"_Team",
        "team_password":''.join(random.choice(charset) for i in range(12)),
    }
    return user

def Auth_needed(url):
    resp = requests.get('%s/api/v1/challenges'%url, allow_redirects=False).text
    if('success": true' in resp):
        return False
    return True

def Derive(word):
    funcs = [
        lambda word:word,
        lambda word:word[0].upper()+word[1:].lower(),
        lambda word:word.lower(),
        lambda word:word.upper()
    ]
    regex = [r'',r'[^\w]',r'[\d]',r'[\d]+[^\w]']
    return list(dict.fromkeys([re.sub(x,'', w(word)) for x in regex for w in funcs]))


def Check_Similarity(team,user):
    variation_user = [] 
    for word in user.split(' ')+['team']:
        variation_user += Derive(word)
    for t in Derive(team):
        for u in variation_user:
            if(u in t):
                return True
    return False

def Sort_Submit(challenges,submissions):
    logger('Sorting all submissions ...','info',1,0)
    all_challenges = {}
    with progress.Progress() as p:
        progress_bar = p.add_task("", total=len(challenges))
        for id_,data in challenges.items():
            all_challenges[id_] = {
                'name':data['name'],
                'category':data['category'],
                'value':data['value'],
                'solves':sorted(
                    [
                        {
                            'date':submit['date'],
                            'team':submit['team']['name'],
                            'team_id':submit['team']['id'],
                            'solved_by':submit['solved_by']
                        } for submit in submissions if submit['challenge_id'] == id_
                    ],
                    key=lambda d: d['date']
                )
            }
            p.update(progress_bar, advance=1)
    total = sum([len(x['solves']) for x in all_challenges.values()])
    logger('%s submissions sorted'%total,'progress',0,1)
    return all_challenges