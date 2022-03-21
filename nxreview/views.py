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
    xmlTopicList = openAndParseXML('test.xml')

    Topic.objects.all().delete()
    Conflict.objects.all().delete()

    #Go through the tag list and add it to the Topic database list
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

        #make sure topic is not marked to be removed already
        for rid in topicIDsToRemove:
            if topic.id == rid:
                continue

        conflicts = []
        #get a list of possible conflicts for this topic
        for comparison in Topic.objects.all():
            if topic.id == comparison.id:
                continue
            
            comparisonTitle = [comparison.title]
            closeMatchList = difflib.get_close_matches(topic.title, comparisonTitle, cutoff=0.7)
            if len(closeMatchList) > 0:
                conflicts.append(comparison)

        #save the conflicts and remove them from the main list 
        if len(conflicts) > 0:
            possibleConflicts = []
            possibleConflictIDs = []
            for conflicting in conflicts:
                #add each to Conflict list
                conflict = Conflict()
                conflict.title = conflicting.title
                conflict.text = conflicting.text  
                conflict.save()
                #add each to local list
                possibleConflicts.append(conflict)
                possibleConflictIDs.append(conflict.id)
                #mark topic for removal from Topic list
                topicIDsToRemove.append(conflicting.id)

            resolvedMap[topic.id] = possibleConflictIDs

            #add a map entry
            conflictMap[len(topicsWithConflicts)] = possibleConflicts
        
            #add topic to local list of conflicting topics
            topicsWithConflicts.append(topic)

    #go through the list and actually remove the topics which are in conflict 
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

       
        for key, value in request.POST.items():
            #only process numberic entries 
            if key.isnumeric() == False:
                continue

            #find the topic in question
            originalTopic = Topic.objects.filter(id=key).first()
            if originalTopic == None:
                continue

            #check if a possible resolution is found, if not check if the value is none, if not go on to next topic
            if value == "none" or value.isnumeric() == False:
                    #no resolution needed, just leave the topic as is
                    continue

            #merge the resolutions into the original topic
            for resolutionID in value:
                resolution = Conflict.objects.filter(id=resolutionID).first()
                if resolution == None:
                    continue
                
                originalTopic.text += "\n" + resolution.text
                originalTopic.save()

                #remove entry from resoution map
                for resID in resolvedMap[key]:
                    if resolutionID == resID:
                        resolvedMap[key].remove(resolutionID)

                #remove the topic from the conflict list
                resolution.delete()

        #move the remaining topics on the conflict list into the main list
        for conf in Conflict.objects.all():
            newTopic = Topic()
            newTopic.text = conf.text
            newTopic.title = conf.title
            newTopic.save()
        Conflict.objects.all().delete()    
           

        #after all conflicts have been resolved, rewrite the xml with no repeats 
        tree = ET.parse('rtest.xml')
        root = tree.getroot()
        root.clear()
        for item in Topic.objects.all():
            e = ET.Element(item.title.strip())
            e.text = "\r\t\t"+item.text.strip()+"\n\t"
            root.append(e)

        #prettyfy and save the xml
        prettyXMLStr = minidom.parseString(ET.tostring(root)).toprettyxml(newl="\n\n")
        with open("RewriteReview.xml", "w") as f:
            f.write(prettyXMLStr)
            
        
        #go back to main page
        return redirect('nxreview:index') 

    else:
        return render(request, 'conflicts.html')

 

                  
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




        

        
    
  