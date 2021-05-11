import os
import random
import json
import argparse
from ftfy import fix_text
from pprint import pprint

parser = argparse.ArgumentParser()
parser.add_argument('--source-file', required=True)
args = parser.parse_args()

with open(args.source_file) as data_file:
    game_data = json.load(data_file)

rounds = ('jeopardy', 'double-jeopardy', 'final-jeopardy')

options = [3,4,5,8,9,10,13,14,15,18,19,20,23,24,25,28,29,30]

daily_double1 = random.choice(options)
options.remove(daily_double1)
daily_double2 = random.choice(options)
options.remove(daily_double2)
daily_double3 = random.choice(options)
options.remove(daily_double3)

jeopardy_categories = ('HAPPY NEW YEAR', 'FUN WITH STATE NAMES', 'ROME, THE ETERNAL CITY', 'CAMPING', 'LEAD')
jeopardy_show = ('5136', '6167', '5663', '4553', '5488')
jeopardy_values = (200, 400, 600, 800, 1000)

double_jeopardy_categories = ('HAPPY NEW YEAR', 'ADD A LETTER', 'ITALIAN CITIES', 'IVY LEAGUERS', 'CHRISTMAS MOVIES')
double_jeopardy_show = ('5599', '4157', '3145', '4531', '5361')
double_jeopardy_values = (400, 800, 1200, 1600, 2000)

final_jeopardy_category = ''
final_jeopardy_show = ''
formatted_data = { "jeopardy": [], "double-jeopardy": [], "final-jeopardy": {} }

for round in rounds:
    if round == 'jeopardy':
        round_formatted = 'Jeopardy!'
        i=1
        for category in jeopardy_categories:
            category_object = { "name": category, "questions": [] }
            for value in jeopardy_values:
                for show_number in jeopardy_show:
                    for option in game_data:
                        if option['round'] == round_formatted and option['category'] == category and option['show_number'] == show_number and option['value'] == '$'+str(value):
                            if value >= 600 and i == daily_double1:
                                category_object["questions"].append({ "value": value, "question": fix_text(option['question']), "answer": fix_text(option['answer']), "daily-double": "true" })
                            else:
                                category_object["questions"].append({ "value": value, "question": fix_text(option['question']), "answer": fix_text(option['answer']) })
                            i+=1
            formatted_data["jeopardy"].append(category_object)
    print(formatted_data)

    if round == 'double-jeopardy':
        round_formatted = 'Double Jeopardy!'
        i=1 
        for category in double_jeopardy_categories:
            category_object = { "name": category, "questions": [] }
            for value in double_jeopardy_values:
                for show_number in double_jeopardy_show:
                    for option in game_data:
                        if option['round'] == round_formatted and option['category'] == category and option['show_number'] == show_number and option['value'] == '$'+str(value):
                            if value >= 1200 and (i == daily_double2 or i == daily_double3):
                                category_object["questions"].append({ "value": value, "question": fix_text(option['question']), "answer": fix_text(option['answer']), "daily-double": "true" })
                            else:
                                category_object["questions"].append({ "value": value, "question": fix_text(option['question']), "answer": fix_text(option['answer']) })
                            i+=1
            formatted_data["double-jeopardy"].append(category_object)
    print(formatted_data)

    if round == 'final-jeopardy':
        round_formatted = 'Final Jeopardy!'
        for option in game_data:
            if option['round'] == round_formatted and option['show_number'] == final_jeopardy_show and option['category'] == final_jeopardy_category:
                formatted_data["final-jeopardy"]["category"] = final_jeopardy_category
                formatted_data["final-jeopardy"]["question"] = fix_text(option['question'])
                formatted_data["final-jeopardy"]["answer"] = fix_text(option['answer'])
    print(formatted_data)

name, ext = os.path.splitext(args.source_file)
outfile_name = "{name}_{uid}{ext}".format(name=name, uid='formatted', ext=ext)

with open(outfile_name, 'w') as outfile:
    json.dump(formatted_data, outfile, indent=4)
