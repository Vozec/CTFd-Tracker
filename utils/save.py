#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# _authors_: Vozec
# _date_ : 20/08/2022

import os,os.path,json
from utils.misc	import Resolve_CTF

def Save(args,to_save):
	directory = Init(args)
	for name,data in to_save.items():
		if(data != {}):
			open('%s/%s/%s.json'%(directory,data[0],name),'w').write(json.dumps(data[1],indent=4))

def Init(args):
	name = args.output if(args.output) else Resolve_CTF(args.url).replace(' ','_')
	if(not os.path.exists(name)):
		path = name
	else:
		i = 0
		path = '%s_%s'%(name,i)
		while(os.path.exists(path)):
			i += 1
			path = '%s_%s'%(name,i)
	os.makedirs('%s/scraped_data'%path,exist_ok=True)
	os.makedirs('%s/analyzed_data'%path,exist_ok=True)
	return path