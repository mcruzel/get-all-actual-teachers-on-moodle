# get-all-actual-teachers-on-moodle
List teachers in Moodle

This script will export a csv file with all actual teachers on Moodle, following this structure :

| userid | firstname+lastname | email                    |
|--------|--------------------|--------------------------|
| 1      | Paul DUPONT        | paul.dupont@myschool.com |
| etc... |                    |                          |

The script eliminates duplicates on list.

This is particularly useful if you have course archives and admins enrolled in some courses on Moodle, and you want to have an up-to-date list of teachers on your LMS.

# Librairies

This script use the following python librairies :

requests
json
os
csv

# Prerequisites on Moodle

* You need to create a cohort for teachers and regulary fill her (a script may be useful, i'll upload something later about this)
* Custom reports plugin, and 3 reports (check sql files in this git)
  * All courses listing (sql request 1.sql)
  * All categories listing (sql request 2.sql)
  * All teachers listing (sql request 3.sql)
    * You can edit this file for adding others roles for teachers (default : editing_teacher + teacher)
* An account for webservices (login+password), NOT A TOKEN 
