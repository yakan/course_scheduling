
# coding: utf-8

# In[26]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def convert(inputTime):
    # define convert function
    try:
        hh,mm,ss=str(inputTime).split(':')
        ans=int(hh)+int(mm)/60+int(ss)/3600
    except:
        ans=np.nan
    return ans


def loadDataDict(df,roomSet):
    # adding entries to a list instead of finding beginning and end, and adding empty list for unused classrooms
    ans={}
    # Start with empty lists in all classrooms
    terms=[20153,20161,20162,20163,20171,20172]
    for term in terms:
        for room in roomSet:
            for day in 'MTWHF':
                ans[term,room,day]=[]
    for index,row in df.iterrows():   
        term=row['Term']       # Obtain the corresponding column of each row
        room=row['First Room']
        days=row['First Days'] 
        beg=convert(row['First Begin Time'])   # Convert the begin time strings into decimal numbers using challenge 1
        end=convert(row['First End Time'])     # Convert the begin time strings into decimal numbers using challenge 1
        # Skip rows in which beg and end are np.nan (not a number), and in which the room is not in the capacity file
        #import pdb; pdb.set_trace()
        if np.isnan(beg) or np.isnan(end) or room not in roomSet:  
            continue     # Command to skip this iteration of the loop
        for day in 'MTWHF':   # Iterate through the sequence ['M','T','W','H','F']
            if day in days: 
                ans[term,room,day].append([beg,end])
    
    return ans
                    
def computeUsage(inputList, primeStart,primeEnd):
    # sorting the inputList
    sortedList=sorted(inputList)
    usage=0
    prev=0
    for start,end in sortedList:
        if end<primeStart:
            continue
        if start>primeEnd:
            break
        start=max(prev,start)
        end=max(prev,end)
        overlap=max(0,min(primeEnd,end)-max(primeStart,start))
        usage+=overlap
        prev=end
    return usage/(primeEnd-primeStart)

# Beginning of main code.
primeStart=10
primeEnd=16

# Read in data
schedule=pd.read_excel('../data/Marshall_Course_Enrollment_1516_1617.xlsx')
cancelled=pd.read_excel('../data/Cancelled_Courses_1516_1617.xlsx')
master=schedule.append(cancelled)
capacities=pd.read_excel('../data/Marshall_Room_Capacity_Chart.xlsx')

# Set rooms to focus on to be those in the capacity file.
roomSet=set(capacities.Room)

# Load the data from the master DataFrame into a dictionary of the format in challenge 2
dataDict=loadDataDict(master,roomSet)

# Create a list of lists, corresponding to the data we want to dump out. 
lines=[]
for term,room,day in loadDataDict(master,roomSet):
    # Each row of the output data has columns being term, room, day, utilization
    lines.append([term,room,day,computeUsage(dataDict[term,room,day],primeStart,primeEnd)])

# Store data back into a dataframe
output=pd.DataFrame(lines,columns=['Term','Room','Day','Utilization'])

# Output to a file
output.to_csv('RoomUsage.csv')
output.head()


# In[30]:


output=pd.DataFrame(lines,columns=['Term','Room','Day','Utilization']).merge(capacities[['Room','Size']], on='Room')  # Merge room size data with the generated output above
output['Label']=output.Room.str.cat(output.Size.astype(str),sep=' ') # Create labels of room number + room capacity

for term in [20163,20171]:
    for day in 'MTWHF':
        (output.query("Term==@term & Day==@day")
         .sort_values(['Room'])
         .plot(x='Label',y='Utilization',by='Day',kind='bar', title='{0} {1}'.format(term,day),figsize=(18,4),ylim=(0,1),legend=False)
        )
plt.show()


# In[24]:


for term in [20163,20171]:
    for day in 'MTWHF':
        (output.query("Term==@term & Day==@day")
         .sort_values(['Utilization','Room'])
         .plot(x='Label',y='Utilization',by='Day',kind='bar',title='{0} {1}'.format(term,day),figsize=(18,4),ylim=(0,1),legend=False)
        )
plt.show()


# In[25]:


# Create a mapping between rooms as well as indices in the sorted order
rooms=sorted(list(capacities.Room))
roomsMap={rooms[ind]:ind for ind in range(len(rooms))}

# Iterate through the dataDict dictionary and store the data instead in dictionaries indexed by (term,day)
# For each course, the x dictionary stores the index of the room, ymin the begin time, ymax the end time.
x={}
ymin={}
ymax={}
for term,room,day in dataDict:
    for beg,end in dataDict[term,room,day]:
        if (term,day) not in x:
            x[term,day]=[]
            ymin[term,day]=[]
            ymax[term,day]=[]
        x[term,day].append(roomsMap[room])
        ymin[term,day].append(beg)
        ymax[term,day].append(end)

# Display the above data using matplotlib.vlines.
for term in [20163,20171]:
    for day in 'MTWHF':
        if (term,day) in x:
            plt.figure(figsize=(18,8))
            plt.xticks(range(len(rooms)),rooms,rotation=90)
            plt.title('Schedule for {0} {1}'.format(term,day))
            plt.gca().invert_yaxis()
            plt.vlines(x[term,day],ymin[term,day],ymax[term,day])
plt.show()
#plt.close('all')

