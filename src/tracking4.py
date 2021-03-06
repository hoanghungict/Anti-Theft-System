''' 
Container content :

humanDataset         = {human_id1:humanData1, human_id2:humanData2, ...}
itemDataset          = {item_id1:itemData1, item_id2:itemData2, ...}
missingPeopleDataset = {feature1:humanData1, feature2:humanData2, ...}
detection            = [[upleft_x, upleft_y, downright_x, downright_y],[upleft_x, upleft_y, downright_x, downright_y]...]


function defined:

Scan_for_item_existing()
Tracking_suspect()
Display()

'''
from dataType import humanData,itemData
import numpy as np
import random
import cv2

def Scan_for_item_existing(humanDataset, itemDataset, missingPeopleDataset):
	oclussion_check_dist=300  #not sure about this distance
	stolen_check_dist=300     #Leave larger distance 
	pop_item_list=[]
	pop_human_list=[]
	for human in humanDataset.values():
		print("human info==",human.id, "missing",human.missing, "item list",human.itemList)
		# if human.missing == True:  #True or falsue
		if human.missing > 50: 
			
			for index,item in enumerate(human.itemList):
				if item!=0:
					cloestHuman,dist=findClosestHuman(itemDataset[item],humanDataset)
					if cloestHuman == None:
						# print("no one close")
						continue
					# print("find someone close")
					#print("item",itemDataset[item].id,itemDataset[item].missing)
					if itemDataset[item].missing <=50:
						# print("i want to see this number = ",itemDataset[item].id, itemDataset[item].missing) 
						print("itemflag alarm", itemDataset[item].alarm_flag)
						itemDataset[item].alarm_flag = True
						if item in cloestHuman.stolenitemDict: # when human become suspect but item detect again
							cloestHuman.stolenitemDict.pop(item)
							print("Pop from stolenDict",cloestHuman,"id")
						#if dist>stolen_check_dist:
							cloestHuman.isSuspect[item]=False  
						# if dist>oclussion_check_dist :
						# 	if cloestHuman.isSuspect==True:
						# 		cloestHuman.stolenitemDict[item]=itemDataset[item]
						# 		# if itemDataset[item].missing == 0:
						# 		# 	cloestHuman.isSuspect = False
						# 		# else:
						# 		# 	cloestHuman.stolenitemDict[item]=itemDataset[item]
						# 	#cloestHuman.isSuspect=True 
						# 	#Take by suspect explicitly
						# else:
						# 	#print("in range",cloestHuman.id,dist)
						# 	cloestHuman.isSuspect=True
					else:
						#print("itemflag2",item,itemDataset[item].alarm_flag)
						#print("what are you doing ",itemDataset[item].alarm_flag)
						# print("time to find the suspect")
						if itemDataset[item].alarm_flag == True:
							#cloestHuman,dist=findCloestHuman(item,humanDataset) 
							print("=======alarm item: ",itemDataset[item].id)
							try: 
								if cloestHuman.isSuspect[item]==True:
									print(cloestHuman.id, "is suspect..................")
									if dist>stolen_check_dist:
										cloestHuman.stolenitemDict[item]=itemDataset[item]
										print("add to dict")
								else:


									if dist<oclussion_check_dist:
										print("less than oclussion\n\n\n\n",dist,oclussion_check_dist)
										cloestHuman.isSuspect[item]=True
									#cloestHuman.stolenitemDict[item]=itemDataset[item]
									else:
										print("greter than oclussion\n\n\n\n",dist,oclussion_check_dist)
										cloestHuman.isSuspect[item]=False    
									#Oclussion case
								#else:
								#	cloestHuman.isSuspect=False 
								#Track_and_display(humanDataset) will used in main function   
							except:
								print("false=====")
								cloestHuman.isSuspect[item]=False
								pass
								# print(cloestHuman.id, "isn't suspect yet..................")
								
						else:
							print("pop item when no alarm ",item,"human pos",human.x,human.y)
							pop_item_list.append(itemDataset[item])
							human.itemList.pop(index)

						#print("what is left in human item list",human.id,human.itemList)
							#Pop_item_from_dataset(item,itemDataset)  #minor Case: disappear at same time
			if human.itemList == [] :
				print("pop human",human.id,human.missing,human.itemList)
				pop_human_list.append(human)
				#Pop_human_from_dataset(human,humanDataset)
		else:
			#print("human.item",human.id,human.itemList,human.x,human.y)
			for index,item in enumerate(human.itemList):
				print("human item list ",itemDataset[item].name,"in human",human.id)
				if itemDataset[item].missing >50:
					print("pop item when item missing")
				
					human.itemList.pop(index)
					#Pop_item_from_dataset(item,itemDataset)
					pop_item_list.append(itemDataset[item])
				else:
					itemDataset[item].alarm_flag=False   
	for item in pop_item_list:
		Pop_item_from_dataset(item,itemDataset)
	for human in pop_human_list:
		Pop_human_from_dataset(human, humanDataset, missingPeopleDataset)
		


def Track_and_Display(humanDataset,itemDataset,orig_im,human_detect,item_detect,classes,colors):
	
	img=orig_im	
	human_disp_list={}
	item_disp_list={}
	for human in humanDataset.values():
		print("Suspect",human.id, human.isSuspect, human.stolenitemDict.keys())
		
		if len(human.stolenitemDict)!=0: 
			#bounded with red color
			human_disp_list[(human.x,human.y)]=((51,51,251),human.id)#"red"
		else: 
			#bounded with black color
			# if human.missing ==False:
			if human.missing <=50 :
				human_disp_list[(human.x,human.y)]=((0,0,0),human.id)#"black"


	for item in itemDataset.values():
		
		item_disp_list[(item.x,item.y)]=item.owner#"red"
		
	
	for item,_item_class in zip(item_detect[0],item_detect[1]):

		c1=tuple(item[0:2])
		c2=tuple(item[2:4])
		cls=_item_class
		#inx = (item[0] + item[2])/2.0
		#iny = (item[1] + item[3])/2.0
		#owner=item_disp_list[(inx,iny)]
		color = random.choice(colors)
		cv2.rectangle(img, c1, c2,color, 1)		
		#t_size = cv2.getTextSize(cls+" owned by " +str(owner), cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]
		t_size = cv2.getTextSize(cls, cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]
		c2 = c1[0] + t_size[0] + 3, c1[1] + t_size[1] + 4
		cv2.rectangle(img, c1, c2,color, -1)
		cv2.putText(img, cls, (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [225,255,255], 1);
			
			
	for human,_human_class in zip(human_detect[0],human_detect[1]):
		c1=tuple(human[0:2])
		c2=tuple(human[2:4])
		cls=_human_class
		hnx = (human[0] + human[2])/2.0
		hny = (human[1] + human[3])/2.0
		color,hid=human_disp_list[(hnx,hny)]
		#print("====color",color)
		cv2.rectangle(img, c1, c2,color, 1)		
		t_size = cv2.getTextSize(cls+"  ", cv2.FONT_HERSHEY_PLAIN, 2 , 1)[0]
		c2 = c1[0] + t_size[0] + 3, c1[1] + t_size[1] + 4
		cv2.rectangle(img, c1, c2,color, -1)
		if color!=(0,0,0):#BLACK
			cv2.putText(img, "Suspect"+str(hid), (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 2, [225,255,255], 1);
		else:
			cv2.putText(img, cls+str(hid), (c1[0], c1[1] + t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 2, [225,255,255], 1);

		#print("human",human,_human_class)





def Pop_item_from_dataset(item,itemDataset):
	#print("itemDataset",itemDataset)
	#print("item",item.id)
	itemDataset.pop(item.id) # typo: pop() need to use key not value
def Pop_human_from_dataset(human,humanDataset,missingPeopleDataset):
	print("missing",missingPeopleDataset,human)
	humanDataset.pop(human.id) # typo: pop() need to use key not value
	missingPeopleDataset.remove(human)


def findClosestHuman(item,humanDataset):
	min_dist=10000
	dist = 10000 # add by yes, dist need to be initialize otherwise when no human will error
	closestHuman=None
	for human in humanDataset.values():
		if human.missing <=50:
			dist=np.sqrt((item.x-human.x)**2+(item.y-human.y)**2)
			if dist<min_dist:
				min_dist=dist
				closestHuman=human
	return closestHuman,dist
