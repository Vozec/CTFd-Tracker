#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

from utils.scraper import Scrape_Statistics
import json

def Create_Links(challenges,statistics,maxdiff=5):
	links_tt , links_ut = {},{}

	for challenge_id, dump in challenges.items():
		config = {
			'value':dump['value'],
			'solves':statistics[challenge_id]['solves'],
			'percentage':statistics[challenge_id]['percentage']
		}

		dump['total_solves'] = config['solves']
		dump['percentage']  = config['percentage']

		if(len(dump['solves']) > 1):
			for i in range(1,len(dump['solves'])):
				flag_current = dump['solves'][i]
				previous 	 = dump['solves'][max(0,i-maxdiff):i]
				for flag_before in previous:
					links_tt,links_ut = Linker(links_tt,links_ut,flag_current,flag_before,config)

	links_tt,links_ut = Sort_links(links_tt),Sort_links(links_ut)
	return challenges,links_tt,links_ut




def Linker(links_tt,links_ut,current,before,config):
	diff 	  			 	 = abs(current['date']-before['date'])
	score	  			 	 = Calculate_Score(diff,config)
	current_name,before_name = current['team'],before['team']
	flagger 			 	 = current['solved_by']['name']
	links_tt 			 	 = Update_dict(links_tt,score,current_name,before_name)
	links_ut 				 = Update_dict(links_ut,score,flagger,before_name)
	return links_tt,links_ut

def Update_dict(dico,score,current_name,before_name):
	dico[current_name] = dico.setdefault(current_name,{})
	dico[current_name][before_name] = dico[current_name].setdefault(before_name,score) + score
	return dico

def Calculate_Score(diff,config):
	return ((config['value']//10) / (diff // 60))* (1-config['percentage'])

def Sort_links(dico):
	return sorted(
		dict((name,dict(sorted(
				data.items(), 
				reverse=True,
				key=lambda item: item[1]
			))) 
		for name,data in dico.items()
		).items(),
			key=lambda x: list(x[1].values())[0],
			reverse=True)