#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

from rich import progress

from utils.logger import logger
from utils.misc	  import Resolve_user,Check_Similarity

def Detect_team_accounts(teams,users,url):
	spotted = {}
	if(len(teams) > 0):
		logger('Detecting team accounts...','info',1,0)		
		spotted['shared_account'] = []
		with progress.Progress() as p:
			progress_bar = p.add_task("", total=len(teams))
			
			for id_team,team_data in teams.items():
				names , name_team	 = [] , team_data['name']
				for id_user in team_data['members']:
					names.append(users[Resolve_user(id_user,users)]['name'])
				for username in names:
					if (Check_Similarity(name_team,username)):
						spotted['shared_account'].append({
							'team':name_team,
							'link':'%s/teams/%s'%(url,id_team),
							'users':names
							})
						break

				p.update(progress_bar, advance=1)

		logger('%s team accounts detected'%len(spotted['shared_account']),'progress',0,1)
		for spot in spotted['shared_account']:
			logger('%17s | %25s | %s'%(tuple(spot.values())),'error',0,0)
	return spotted


def Detect_flag_hoarding(submissions,limit=1/8):
	logger('Detection of teams doing flag hoarding ...','info',1,0)
	spotted = {'hoarding_flag_team':[]}
	start,end = 0,0
	with progress.Progress() as p:
		progress_bar = p.add_task("", total=len(submissions))
		all_date = [x['date'] for x in submissions]
		start,end = min(all_date),max(all_date)
		average = {}

		for sub in submissions:
			if sub['team']['name'] not in average.keys():
				average[sub['team']['name']] = {'sum':0,'count':0,'average':0}

			data 			= average[sub['team']['name']]
			data['sum']    += sub['date']
			data['count']  += 1
			data['average'] = data['sum'] // data['count']

			if(start > sub['date']):start = sub['date']
			if(end   < sub['date']):end   = sub['date']

			p.update(progress_bar, advance=1)

	for team,data in average.items():
		if( (start+(end-start)*limit) < data['average']):
			spotted['hoarding_flag_team'].append((
				team,
				'https://demo.ctfd.io/teams/%s'%team,
				data['average']
				))

	logger('%s team spotted'%len(spotted['hoarding_flag_team']),'progress',0,1)
	for spot in spotted['hoarding_flag_team']:
		logger('%17s | %25s | %s'%(tuple(spot)),'error',0,0)

	return spotted

