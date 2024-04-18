import json
import requests
from bs4 import BeautifulSoup
import re

classes = list
with open("classes_modified.txt","r") as f:
    contents = f.read()
    classes = json.loads(contents)
# labels = ["class","section","call number","people enrolled","professor","idk","idk","idk \''","classfn"]
# daysofweek = ["Sun","Mon","Tues","Weds","Thurs","Fri","Sat"]
courses_offered = {}
sections_offered = {}
section_data = {}
professor_rating = {}
url_professor_rating = "https://www.ratemyprofessors.com/search/professors/668?q="
def split_course(course) -> int:
    return next((i for i, c in enumerate(course) if not c.isupper()), -1)
def seconds_to_time(seconds):
    return "{:02d}:{:02d}".format(int(seconds // 3600), int((seconds % 3600) // 60))
def get_rating(name) -> float:
    names = name.split(",")
    first_name = names[1].strip()
    last_name = names[0].strip()
    url = url_professor_rating+first_name+"%20"+last_name
    page = requests.get(url)
    soup = BeautifulSoup(page.content,"html.parser")
    scripts = soup.find_all("script")
    curr_script = 0
    avg_rating = 0
    legacy_id = 0
    lst = {}
    for sc in scripts: 
        script_text = str(sc)
        match = re.search(r'"legacyId":(\d{7})', script_text) 
        if match:
            legacy_id = match.group(1)
            lst['legacyID'] = legacy_id
            if name not in professor_rating:
                professor_rating[name] = []
            professor_rating[name].append(legacy_id) 

        else:
            legacy_id = "N/A"

        rating_match = re.search(r'"avgRating":(\d+(?:\.\d{1,2})?)', script_text)
        if rating_match:
            avg_rating = float(rating_match.group(1))
            lst['averageRating'] = avg_rating


        school_patt = r'"name":\s*"([^"]+)"'
        school_match = re.search(school_patt, script_text)
        if school_match:
            lst['school'] = school_match.group(1)
        curr_script+=1
    return lst

with open("classes_modified.txt","r") as f: 
    for a in range(0,len(classes)):
    # for a in range(700,710):
        index_to_slice = split_course(classes[a][0])
        if classes[a][0][:index_to_slice] not in courses_offered:
            courses_offered[classes[a][0][:index_to_slice]] = [classes[a][0][index_to_slice:]]
        else:
            courses_offered[classes[a][0][:index_to_slice]].append(classes[a][0][index_to_slice:])
        for i in range(3,len(classes[a])):
            for o in range(len(classes[a][i])):
                if(o <= 8):
                    if classes[a][0] not in sections_offered:
                        sections_offered[classes[a][0]] = [classes[a][i][1]]
                    elif classes[a][i][1] not in sections_offered[classes[a][0]]:
                        sections_offered[classes[a][0]].append(classes[a][i][1])
                else:
                    for day in classes[a][i][o]:
                        hour_start = int(day[1] / 3600)
                        minutes_start = int(float((day[1] % 3600)/60))
                        hour_end = int(day[2]/3600)
                        minutes_end = int(float((day[2] % 3600)/60))
                        course = classes[a][0]
                        section = classes[a][i][1]
                        full = course+section
                        if full not in section_data:
                            section_data[full] = [day[0],day[1],day[2],day[3],classes[a][i][4]]
                            if classes[a][i][4] not in professor_rating and classes[a][i][4] != None:
                                professor_rating[classes[a][i][4]] = get_rating(classes[a][i][4])
                        else:
                             section_data[full].extend([day[0],day[1],day[2],day[3],classes[a][i][4]])

f.close()

# with open("course_structure.json","w") as f:
#     json.dump(section_data,indent=3,fp=f)
# f.close()

# with open("professor_ratings.json","w") as f:
#     json.dump(professor_rating,indent=3,fp=f)
# f.close()

















"""
will always start with 3 basic datas (class abbrev. class full name. credits.)
0. class abbrev. 
1. class full name.
2. number of credits.
this will be followed by arrays each representing a section
within each section array it will always follow 9 basic datas
0. class abbrev. (ACCT115)
1. call # (90001)
2. section number. (001)
3. people enrolled (1/15)
4. professor (Micale, Joseph)
5. idk (0)
6. idk (0)
7. idk ('')
8. class full. (FUND OF FINANCIAL ACCOUNTING)
after this is subarrays where each represents the day of week
e.g. 
if length = 1 (it is taught for one day with info such as hours,day,etc)
if length = 2 (it is taught for 2 days ....)
etc.
"""

