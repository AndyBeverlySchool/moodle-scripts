#!/usr/bin/env python
import json
import pymysql.cursors
import requests

with open('secure.json') as config_file:
    config = json.load(config_file)

config['mysql'].update({"cursorclass": pymysql.cursors.DictCursor})
cn = pymysql.connect(**config['mysql'])


class MoodleHelper:
    cfg = {}
    s = requests.Session()

    def set_visibility(self, course_id, section_id, value):
        self.s.post(config["moodle_host"] + "course/rest.php",
                    data={"sesskey": self.cfg["sesskey"],
                          "class": "section",
                          "field": "visible",
                          "id": section_id,
                          "courseId": course_id,
                          "value": value})

    def login(self):
        resp = self.s.post(config["moodle_host"] + "login/index.php",
                           {"username": config['u'], "password": config['p']})

        # moodle's internal REST calls require a "sesskey," which is just a random string seemingly assigned at login
        # it is communicated to JS-land via a object stored on M.cfg
        cfg_block_start = resp.content.find("M.cfg =")
        cfg_block_json_start = resp.content.find("{", cfg_block_start)
        cfg_block_end = resp.content.find(";", cfg_block_start)
        self.cfg.update(json.loads(resp.content[cfg_block_json_start: cfg_block_end]))


mh = MoodleHelper()
mh.login()

with cn.cursor() as cursor:
    cursor.execute("select visible from mdl_course_sections where name like 'exam'")
    currently_visible = cursor.fetchone()["visible"] == 1

if currently_visible:
    print("Exams are currently visible. Making them invisible.")
else:
    print("Exams are currently invisible. Making them visible.")

with cn.cursor() as cursor:
    cursor.execute("select course, section from mdl_course_sections where name like 'exam'")
    for row in cursor.fetchall():
        print "c: %s, s: %s" % (row["course"], row["section"])
        mh.set_visibility(row["course"], row["section"], 0 if currently_visible else 1)
    cursor.execute("select course, section from mdl_course_sections where name like 'exam disabled'")
    for row in cursor.fetchall():
        print "c: %s, s: %s" % (row["course"], row["section"])
        mh.set_visibility(row["course"], row["section"], 1 if currently_visible else 0)
