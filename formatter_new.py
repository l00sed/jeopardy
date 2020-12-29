import os
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

jeopardy_categories = ('PREFIXES', 'PHRASES OF DEATH', 'PIZZA TOPPINGS', 'PITS BURG', 'PRAWNOGRAPHY', 'ADJECTIVES')
jeopardy_show = ('5308', '6261', '4936', '4645', '4908', '5126')
jeopardy_values = (200, 400, 600, 800, 1000)

double_jeopardy_categories = ('ADD A LETTER', 'T"EEN"', 'TENTS', 'THAT SINKING FEELING', "THAT'S A LOAD OF GARBAGE", 'ENDS WITH A BODY PART')
double_jeopardy_show = ('4949', '3846', '3684', '3512', '4228', '6160')
double_jeopardy_values = (400, 800, 1200, 1600, 2000)

final_jeopardy_category = 'AMERICAN WOMEN'
final_jeopardy_show = '6253'
formatted_data = { "jeopardy": [], "double-jeopardy": [], "final-jeopardy": {} }

for round in rounds:
    if round == 'jeopardy':
        round_formatted = 'Jeopardy!'
        for category in jeopardy_categories:
            category_object = { "name": category, "questions": [] }
            for value in jeopardy_values:
                for show_number in jeopardy_show:
                    for option in game_data:
                        if option['round'] == round_formatted and option['category'] == category and option['show_number'] == show_number and option['value'] == '$'+str(value):
                            category_object["questions"].append({ "value": value, "question": fix_text(option['question']), "answer": fix_text(option['answer']) })
            formatted_data["jeopardy"].append(category_object)
    print(formatted_data)

    if round == 'double-jeopardy':
        round_formatted = 'Double Jeopardy!'
        for category in double_jeopardy_categories:
            category_object = { "name": category, "questions": [] }
            for value in double_jeopardy_values:
                for show_number in double_jeopardy_show:
                    for option in game_data:
                        if option['round'] == round_formatted and option['category'] == category and option['show_number'] == show_number and option['value'] == '$'+str(value):
                            category_object["questions"].append({ "value": value, "question": fix_text(option['question']), "answer": fix_text(option['answer']) })
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
