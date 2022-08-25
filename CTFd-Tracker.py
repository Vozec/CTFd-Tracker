#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

import argparse,requests,json

from utils.logger  	 import logger
from utils.misc	 	 import *
from utils.detection import *
from utils.scraper 	 import *
from utils.ctfd		 import Auth_CTFd
from utils.linker    import Create_Links
from utils.save 	 import Save


def parse_args():
	parser = argparse.ArgumentParser(add_help=True, description='This tool is used to detect cheater on ctf ctfd-based by creating score between differents teams.')
	parser.add_argument(metavar='url',dest="url",type=str,help="Ctfd Url")
	parser.add_argument("-t",dest="token"   ,default=None, help="CTFd Token to login")
	parser.add_argument("-u",dest="username",default=None, help="CTFd Username")
	parser.add_argument("-p",dest="password",default=None, help="CTFd Password")
	parser.add_argument("-m",dest="maxdiff",default=5,type=int, help="Maximum number of backtracks for each challenge check")
	parser.add_argument("-o",dest="output",default=None, help="Output Directory")
	args = parser.parse_args()
	return args


def main(args):
	args.url = Cleaner_url(args.url)
	if(Check_Ctfd(args.url)):

		session = requests.session()
		if(Auth_needed(args.url)):
			Auth_CTFd(args,session)

		if(session):
			to_save = {}

			teams  				   		 = Scrape_teams(session,args.url)
			users 				   		 = Scrape_users(session,args.url)
			submissions,challenges 		 = Scrape_Submissions(session,args.url,teams)

			if(len(submissions) > 0):

				challenges	   		   		 = Sort_Submit(challenges,submissions)
				statistics 			   		 = Scrape_Statistics(session,challenges,users)
				challenges,links_tt,links_ut = Create_Links(challenges,statistics,args.maxdiff)
				
				to_save['All_users'] 		= ['scraped_data',users]
				to_save['All_teams'] 		= ['scraped_data',teams]
				to_save['Scoreboard']		= ['scraped_data',Scrape_Scoreboard(session,args.url)]
				to_save['All_solves'] 		= ['scraped_data',challenges]

				to_save['All_links_T2T'] 	= ['analyzed_data',links_tt]
				to_save['All_links_U2T'] 	= ['analyzed_data',links_ut]
				to_save['Shared_account']	= ['analyzed_data',Detect_team_accounts(teams,users,args.url)]
				to_save['Hoarding_teams'] 	= ['analyzed_data',Detect_flag_hoarding(submissions)]


				Save(args,to_save)
			else:
				logger('Failed to scrape all submissions !','error',1,0)
	else:
		logger('%s seems to not be ctfd-based !'%args.url,'error',1,0)
	return 0

if __name__ == '__main__':
	header()
	main(parse_args())