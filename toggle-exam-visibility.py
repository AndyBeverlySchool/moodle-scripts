import json
import pymysql.cursors

with open('secure.json') as config_file:
    config = json.load(config_file)

cn = pymysql.connect(**config['mysql'])

with cn.cursor() as cursor:
    cursor.execute("select visible from mdl_course_sections where name like 'exam'")
    currently_visible = cursor.fetchone()[0] == 1

if currently_visible:
    print("Exams are currently visible. Making them invisible.")
else:
    print("Exams are currently invisible. Making them visible.")

with cn.cursor() as cursor:
    cursor.execute("update mdl_course_sections set visible = %s where name like 'exam'",
        (0 if currently_visible else 1,))
    cursor.execute("update mdl_course_sections set visible = %s where name like 'exam disabled'",
        (1 if currently_visible else 0,))
    cn.commit()
