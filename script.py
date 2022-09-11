import requests
import json
import os
import csv

global reportid_categories
global reportid_courses
global reportid_teacher_list
global teacher_cohortid
reportid_categories = 0 # fill this
reportid_courses = 0 # fill this
reportid_teacher_list = 0 # fill this
teacher_cohortid = 0 # fill this

def request_ws(ws, param_request):
    login = "" # fill this
    password = "" # fill this
    url_moodle = "" # fill this
    request = url_moodle+"webservice/rest/simpleserver.php?wsusername="+str(login)+"&wspassword="+str(password)+"&moodlewsrestformat=json&wsfunction="+ws+param_request
    webservice_reponse_content = requests.get(request)
    webservice_reponse_content_py = json.loads(webservice_reponse_content.text)
    return webservice_reponse_content_py

    
# At the begin : take all courses list from custom reports plugin ws
def get_report_courses():
    ws = "block_configurable_reports_get_report_data"
    param_request = "&reportid="+str(reportid_courses)
    webservice_reponse_content_courses_py = request_ws(ws, param_request)
    ws_courses_data = webservice_reponse_content_courses_py['data']
    ws_courses_data = json.loads(ws_courses_data)
    return ws_courses_data

# At the begin : take all categories list from custom reports plugin ws
def get_report_categories():
    ws = "block_configurable_reports_get_report_data"
    param_request = "&reportid="+str(reportid_categories)
    webservice_reponse_content_categories_py = request_ws(ws, param_request)
    ws_categories_data = webservice_reponse_content_categories_py['data']
    ws_categories_data = json.loads(ws_categories_data)
    return ws_categories_data

# Get courses and create courses (menu only)
def get_courses_from_report_menu(ws_categories_data, ws_courses_data, category):
    print("Liste des cours actuels de la catégorie "+str(category))
    print("-----------------------")
    menu_choice = 1
    menu_array = []
    for i_courses in ws_courses_data:
        if str(i_courses['category']) == str(category):
            print(str(menu_choice)+" -> "+i_courses['fullname'])
            menu_array.append([menu_choice, i_courses['shortname'], i_courses['fullname']])
            menu_choice += 1
    response_input_menu_cours = input("Taper le numéro du cours dans lequel vous souhaitez ajouter la cohorte. Tapez r pour retourner aux catégories. Tapez launch pour lancer le script. > ")
    if response_input_menu_cours == "r": # if we want to return at category selection
        balayage_categories(ws_categories_data, ws_courses_data, category)
    else:
        menu_choice = int(response_input_menu_cours)

# for categories listing menu
def cut_course_names(coursename):
    if len(coursename)>25:
        course = str(coursename[0:22])+"..."
        return course
    else:
        course = str(coursename)
        return course

# put blank in list course on 3 columns    
def blank_in_menu_display(value, gap):
    x = 0
    blank = ""
    if len(value) < gap:
        blank_value = gap - len(value)
        while x < blank_value:
            blank = blank+" "
            x += 1
    return blank

def get_category_parentid(categoryid, ws_categories_data):
    for category in ws_categories_data:
        if int(category['id']) == int(categoryid):
            return category['parent']

def display_courses(ws_categories_data, ws_courses_data, origin):
    os.system('cls')
    print('-------------------')
    for i_s_cat_array_info in ws_categories_data:
        if i_s_cat_array_info['id'] == str(origin):
            print("Liste des cours dans la catégorie ["+i_s_cat_array_info['name']+"]")
    for course in ws_courses_data:
        if int(course['category']) == int(origin):
            print(".... "+(course['fullname']))
    
    print('-------------------')
    print('Retour à la catégorie : c, retour à la catégorie parente p')
    response_input = input("Votre choix : > ")
    
    if response_input == 'c':
        balayage_categories(ws_categories_data, ws_courses_data, origin)
    else:
        parentid = get_category_parentid(origin, ws_categories_data)
        balayage_categories(ws_categories_data, ws_courses_data, parentid)

def get_courses_list(category, ws_courses_data):
    print("get courses in category id="+str(category))
    course_list_ids = []
    for course in ws_courses_data:
        if int(course['category']) == int(category):
            course_list_ids.append(course['id'])
    print(course_list_ids)
    return course_list_ids

def get_children_categories_list(origin, ws_categories_data):
    print("get category children in category id="+str(origin))
    children_categories_list_ids = []
    for category in ws_categories_data:
        if int(category['parent']) == int(origin):
            children_categories_list_ids.append(category['id'])
    print(children_categories_list_ids)
    return children_categories_list_ids

def scan_subcatagories(origin, course_list, children_list, ws_courses_data, ws_categories_data):
    for category in children_list:
        children_list.extend(get_children_categories_list(category, ws_categories_data))
        course_list.extend(get_courses_list(category, ws_courses_data))
        children_list.remove(category)

def get_all_teachers_list():
    ws = "block_configurable_reports_get_report_data"
    param_request = "&reportid="+str(reportid_teacher_list)
    ws_response = request_ws(ws, param_request)
    ws_response = ws_response['data']
    ws_response = json.loads(ws_response)

    return ws_response
    
def get_teachers_on_course(courseid, course_list, teacherlist):
    for teacher_row in ws_teachers_data: # check into report 
        if int(teacher_row['courseid']) == int(courseid):
            is_in = 0
             # check into teacher list from other function
            for teacher in teacherlist: # teacherlist : couple of id + names + username
                if int(teacher[0]) == int(teacher_row['userid']):
                    is_in = 1 # the teacher already exists in teacherlist, so skip the teacherlist append
            if is_in == 0:
                teacher_userid = teacher_row['userid']
                teacher_names = teacher_row['user_names'] 
                teacher_username = teacher_row['username']
                teacherlist.append([teacher_userid, teacher_names, teacher_username])
    course_list.remove(courseid)       
    
def scan_teachers(origin, ws_courses_data, ws_categories_data):
    course_list = []
    children_list = []
    course_list = get_courses_list(origin, ws_courses_data)
    children_list = get_children_categories_list(origin, ws_categories_data)
    while len(children_list)>0:
        scan_subcatagories(origin, course_list, children_list, ws_courses_data, ws_categories_data)
    
    for course in course_list:
        get_teachers_on_course(course, course_list, teacherlist)
    
    return course_list

# Keep only teachers in teachers courses list
def verif_adm(teacherlist):
    ws = "core_cohort_get_cohort_members"
    param_request = "&cohortids[0]="+str(teacher_cohortid)
    teachers_in_teachercohort = request_ws(ws, param_request)
    teachers_in_teachercohort = teachers_in_teachercohort[0]['userids'] # only 1 cohort in ws response
    is_on_cohort = 0
    
    teachers_to_remove = []
        
    for teacher_in_list in teacherlist: 
        for teacher_in_cohort in teachers_in_teachercohort: # scanning teacher cohort
            if int(teacher_in_list[0]) == int(teacher_in_cohort): # if is in teacher cohort
                is_on_cohort = 1
                break
            
        if is_on_cohort == 0: # if teacher IS not on teacher cohort, we put the teacher in teacher to remove array 
            # (we don't remove directly because we are on a loop which is scanning teacherlist. Remove in teacherlist during loop will cause stupid jumps)
            print("/!\ "+str(teacher_in_list[1])+" is NOT a teacher")
            teachers_to_remove.append(teacher_in_list)
        else:
            print(str(teacher_in_list[1])+" is a teacher")
            is_on_cohort = 0 # reset value (is =1 if the scanned user is a teacher)
    
    # we now delete non-teachers in teacherlist (we are no longer in the loop)
    for teacher_to_remove in teachers_to_remove:
        teacherlist.remove(teacher_to_remove)
        
    return teacherlist
            
    
def export_teacher_listing(teacherlist):
    verif_adm(teacherlist)
    consolided_teacherlist = [] # list without duplicates
    duplicate = 0
    for teacher in teacherlist:
        for teacher_c in consolided_teacherlist:
            if teacher[0] == teacher_c[0]:
                duplicate = 1
                break
        if duplicate == 0: # there isn't this teacherlist row in consided teacher list
            consolided_teacherlist.append(teacher)
            duplicate = 0
    
    # export in csv
    print(consolided_teacherlist)
    with open('teacher_list.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = ['userid', 'nom et prénom', 'mail']
        writer.writerow(header)
        writer.writerows(consolided_teacherlist)
    print("Fichier csv créé")
        
    
def balayage_categories(ws_categories_data, ws_courses_data, origin):
    # select categories in which duplicate courses
    #f = open("fichierjson.json", "r")
    #json_content_from_file = json.load(f)
    count = 1
    menu_choices = [] # the array with data behing every menu choice
    response_input = ""
    origin = int(origin)
    # Indicates where we are (category)
    print("--------------")
    if origin == 0:
        print("Balayage de la catégorie [Root]")
        category_inside = "Root"
    else:
        for i_s_cat_array_info in ws_categories_data:
            if i_s_cat_array_info['id'] == str(origin):
                print("Balayage de la catégorie ["+i_s_cat_array_info['name']+"]")
                category_inside = str(i_s_cat_array_info['name'])
     
    # choices array building
    for i_s_cat_array in ws_categories_data:
        if i_s_cat_array['parent'] == str(origin):
            print(str(count)+" -> "+i_s_cat_array['name'])
            menu_choices.append([count, i_s_cat_array['name'], i_s_cat_array['id'], i_s_cat_array['parent']])
            courses_display = [] # array for course listing (display in 3 columns) -> empty array
            for i_courses in ws_courses_data:
                if i_courses['category'] == i_s_cat_array['id']:
                        if len(courses_display) < 3: # array for course listing (display in 3 columns) -> filling array
                            courses_display.append(i_courses['fullname'])
                        elif len(courses_display) == 3: # array for course listing (display in 3 columns) -> display array
                            course1 = cut_course_names(courses_display[0])
                            blank1 = blank_in_menu_display(course1, 25)
                            course2 = cut_course_names(courses_display[1])
                            blank2 = blank_in_menu_display(course2, 25)
                            course3 = cut_course_names(courses_display[2])
                            blank3 = blank_in_menu_display(course3, 25)
                            print("        "+course1+blank1+"  |  "+course2+blank2+"  |  "+course3+blank3)
                            courses_display = []
            # array for course listing (display in 3 columns) -> display the rest (<3 units)
            if len(courses_display) == 1:
                print("        "+courses_display[0])
            elif len(courses_display) == 2:
                course1 = cut_course_names(courses_display[0])
                course2 = cut_course_names(courses_display[1])
                print("        "+course1+"  |  "+course2+"  |  ")
            elif len(courses_display) == 0:
                f = 0
            else:
                print("        "+str(courses_display))
                    
            count += 1
    print("Choisir la catégorie à explorer (taper le numéro du menu puis entrée). Taper \"t-categorie\" (exemple : t-3) pour scanner tous les enseignants de cette catégorie. p : retour parent, v : voir les cours de cette catégorie")
    print("-e : export en csv")
    print("--------------")
    response_input = input("Votre choix > ")
    
    if len(response_input.split('-')) > 1: # there is an argument
        # scan teachers in category
        if len(response_input.split('t-')) > 1: 
            category_in_menu = response_input.split('t-')[1]
            for i in menu_choices:
                if i[0] == int(category_in_menu):
                    selected_category = i[2]
                
            print("Let's scan category id="+str(selected_category))
            print(scan_teachers(selected_category, ws_courses_data, ws_categories_data))
            balayage_categories(ws_categories_data, ws_courses_data, origin)
        # export
        elif len(response_input.split('-e')) > 1:
            export_teacher_listing(teacherlist)
        else: # in case of keyboard error
            balayage_categories(ws_categories_data, ws_courses_data, origin)
    elif response_input == "p":
        if origin == 0:
            parentid = 0
        else:
            parentid = get_category_parentid(origin, ws_categories_data)
        balayage_categories(ws_categories_data, ws_courses_data, parentid)
    elif response_input == "v":
        display_courses(ws_categories_data, ws_courses_data, origin)
    elif response_input.isdigit() == True : # if we choiced a category
        for i in menu_choices:
            if i[0] == int(response_input):
                catIDchoiced = i[2]
                balayage_categories(ws_categories_data, ws_courses_data, catIDchoiced)
    else: # if keyboard error
        balayage_categories(ws_categories_data, ws_courses_data, origin)
        
    
    
def main(init = 0):
    if init != 0:
        ws_courses_data = get_report_courses()
        ws_categories_data = get_report_categories()
        global ws_teachers_data
        ws_teachers_data = get_all_teachers_list()
        global teacherlist
        teacherlist = []

    balayage_categories(ws_categories_data, ws_courses_data,  0)
    
main(1)
