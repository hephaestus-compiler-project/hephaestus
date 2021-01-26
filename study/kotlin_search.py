import requests
import json


data = []
first = True
skip = 0
top = 2500
temp_data = []
while len(temp_data) > 0 or first:
    first = False
    print('fetching ' + str(skip))
    response = requests.get('https://youtrack.jetbrains.com/api/issues?query=project:%20Kotlin%20State:%20Fixed%20Type:%20Bug&fields=$type,created,customFields($type,id,name,projectCustomField($type,field($type,fieldType($type,id),id,localizedName,name),id),value($type,id,name)),description,id,idReadable,numberInProject,resolved,summary,updated,tags,project,reporter($type,id,login,name,ringId)&$skip='+ str(skip) + '&$top=2500')
    temp_data = response.json()
    data.extend(temp_data)
    skip += top


print('writing data')
with open('kotlin.json', 'w') as f:
    f.write(json.dumps(data))
