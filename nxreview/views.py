from typing import Sized
from django.shortcuts import render, redirect
from .models import Topic, Conflict
import xml.etree.ElementTree as ET
from xml.dom import minidom
import difflib
from .forms import ConflictResolutionForm

# Create your views here.
def index(request):
    """Home page view"""
    
    #Parse xml files to produce a list of all tags
    xmlTopicList = openAndParseXML('Review.xml')

    Topic.objects.all().delete()
    Conflict.objects.all().delete()

    #Go through the xml tag list and add it to the Topic list
    for xmlTopic in xmlTopicList:
        topic = Topic()
        topic.title = xmlTopic.title
        topic.text = xmlTopic.text
        topic.save()

    #Go through the topic list and for each item check it with every other item on the list
    conflictMap = {}
    topicsWithConflicts = []
    topicIDsToRemove = []
    for topic in Topic.objects.all():
        conflicts = []
        #for each topic get a list of possible conflicts
        for comparison in Topic.objects.all():
            if topic.id == comparison.id:
                continue
            #make sure topic is not marked to removed already
            isRemoved = False
            for tid in topicIDsToRemove:
                if topic.id == tid:
                    isRemoved = True
                
            if isRemoved == True:
                continue

            comparisonTitle = [comparison.title]
            closeMatchList = difflib.get_close_matches(topic.title, comparisonTitle, cutoff=0.7)
            if len(closeMatchList) > 0:
                conflicts.append(comparison)
        if len(conflicts) > 0:
            possibleConflicts = []
            for conflicting in conflicts:
                #add each to Conflict list
                conflict = Conflict()
                conflict.title = conflicting.title
                conflict.text = conflicting.text  
                conflict.save()
                #add each to local list
                possibleConflicts.append(conflict)
                #mark topic for removal from Topic list
                topicIDsToRemove.append(conflicting.id)
                

            #add a map entry
            conflictMap[len(topicsWithConflicts)] = possibleConflicts
            
           

            #add topic to local list of conflicting topics
            topicsWithConflicts.append(topic)

    #go through the list and actually remove the topics 
    for tid in topicIDsToRemove:
        Topic.objects.filter(id=tid).delete()           

    #send conflict list and resolution map for user review
    if len(topicsWithConflicts) != 0:
        context = {'conflictList':topicsWithConflicts, 'closeMatchMap':conflictMap}
        return render(request, 'nxreview/conflicts.html', context)

    else:
        context = {'topics': Topic.objects.all()}
        return render(request, 'nxreview/index.html', context)
   
def conflicts(request):
    if request.method == "POST":

        breakpoint()
        val = 10
        val += 1
  
        #go back to main page
        return redirect('nxreview:index')
    else:
        return render(request, 'conflicts.html')

'''
        for key, value in request.POST.items():
            #check if the new topic is found, if not go on to the next item 
            if key.isnumeric() == False:
                continue
            newTopic = Conflict.objects.filter(id=key).first()
            if newTopic == None:
                continue

            #check if a possible resolution is found, if not check if the value is none, if not go on to next topic
            if value == "none":
                    #no resolution needed, just add the object as is
                    continue
            if value.isnumeric() == False:
                continue
'''
           

'''

        #after all conflicts have been resolved, rewrite the xml with no repeats 
        tree = ET.parse('Review.xml')
        root = tree.getroot()
        root.clear()
        for item in NonConflict.objects.all():
            e = ET.Element(item.title.strip())
            e.text = "\r\t\t"+item.text.strip()+"\n\t"
            root.append(e)

        #prettyfy and save the xml
        prettyXMLStr = minidom.parseString(ET.tostring(root)).toprettyxml(newl="\n\n")
        with open("Review.xml", "w") as f:
            f.write(prettyXMLStr)
            
            
'''
        
        

                
def openAndParseXML(xmlfile):
    tr = ET.parse(xmlfile)
    rt = tr.getroot()
    #Generate a Topic list out of the parsed file
    topicList = []
    for child in rt:
        t = Topic()
        t.title = child.tag
        t.text = child.text
        topicList.append(t)
    return topicList




        

        
    
  