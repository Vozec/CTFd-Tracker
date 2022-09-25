#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

import requests,json
from rich import progress

from utils.logger import logger
from utils.misc   import Convert2Timestamp

def Scrape_teams(session,url):
	logger('Scraping all teams ...','info',1,0)
	all_teams = {}
	try:
		res	= json.loads(session.get('%s/api/v1/teams'%url).text)
		if('message' in res and 'did you mean /api/v1/teams' in res['message']):
			logger('This is a CTF without teams !','error',1,0)
			exit(-1)
		else:
			total_pages = res['meta']['pagination']['pages']
			total 		= res['meta']['pagination']['total']
			with progress.Progress() as p:
				progress_bar = p.add_task("", total=int(total))
				i = 1
				while (i != total_pages+1):
					try:
						res = json.loads(session.get('%s/api/v1/teams?page=%s'%(url,i)).text)
						for team in res['data']:
							rep = json.loads(session.get('%s/api/v1/teams/%s'%(url,team['id'])).text)
							if(1 not in rep['data']['members']):
								all_teams[team['name']] = rep['data']
							p.update(progress_bar, advance=1)
						i += 1
					except:
						logger('Error: Failed to fetch "/api/v1/teams?page=%s"'%i,'error',1,0)
						pass
					
	except Exception as ex:
		logger('Error: Failed to fetch "/api/v1/teams" !','error',1,0)
	logger('%s teams scraped'%len(all_teams),'progress',0,1)
	return all_teams


def Scrape_users(session,url):
	logger('Scraping all users ...','info',1,0)
	all_users = {}
	try:
		res = json.loads(session.get('%s/api/v1/users'%url).text)
		total_pages = res['meta']['pagination']['pages']
		total 		= res['meta']['pagination']['total']
		with progress.Progress() as p:
			progress_bar = p.add_task("", total=int(total))
			i = 1
			while (i != total_pages+1):
				try:
					res = json.loads(session.get('%s/api/v1/users?page=%s'%(url,i)).text)
					for user in res['data']:
						all_users[user['name']] = user
						p.update(progress_bar, advance=1)
					i += 1
				except:
					logger('Error: Failed to fetch "/api/v1/users?page=%s"'%i,'error',1,0)
					pass
	except Exception as ex:
		logger('Error: Failed to fetch "/api/v1/users" !','error',1,0)
	logger('%s users scraped'%len(all_users),'progress',0,1)
	return all_users


def Scrape_Submissions(session,url,teams):
	logger('Scraping all submissions ...','info',1,0)
	challenges , solves  = {} , []
	with progress.Progress() as p:
		progress_bar = p.add_task("", total=len(teams))
		for team in teams.values():
			result = session.get('%s/api/v1/teams/%s/solves'%(url,team['id'])).text
			try:
				res = json.loads(result)
				if('success' in res and res['success']):
					for solve in res['data']:
						challenges[solve['challenge']['id']] = solve['challenge']
						solves.append({
							'team':solve['team'],
							'date':Convert2Timestamp(solve['date']),
							'challenge_id':solve['challenge']['id'],
							'solved_by':solve['user']
						})
			except Exception as ex:
				logger('Error: %s'%ex,'error',1,0)
				print(result)
			p.update(progress_bar, advance=1)
	logger('%s submissions scraped for %s challenges'%(len(solves),len(challenges)),'progress',0,1)
	return solves,challenges



def Scrape_Statistics(session,challenges,users):
	logger('Scraping all statistics ...','info',1,0)
	all_stats = {}
	with progress.Progress() as p:
		total_user = len(users)
		progress_bar = p.add_task("", total=len(challenges.keys()))
		for id_,chall in challenges.items():
			all_stats[id_] = {
				'solves':len(chall['solves']),
				'percentage' : (len(chall['solves']) / total_user)
			}			
			p.update(progress_bar, advance=1)
	logger('All statistics scraped for %s challenges'%len(challenges),'progress',0,1)
	return all_stats

def Scrape_Scoreboard(session,url):
	logger('Scraping the Scoreboard ...','info',1,0)
	res = json.loads(session.get('%s/api/v1/scoreboard'%(url)).text)
	return res['data']
