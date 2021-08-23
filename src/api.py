import flask
import math
import pandas as pd

from flask import request, jsonify
from nltk.tokenize import word_tokenize

FOOD_FILE = "../data/fndds_nutrition.xlsx"
MINIMAL_INTAKE_FILE = "../data/minimal_nutrition_intake.xlsx"
FOOD_CODE = "Food code"
MAIN_FOOD_DESCRIPTION = "Main food description"
LOWER = "Lower"
UPPER = "Upper"
GENDER = "Gender"
FOOD_NAME = "food_name"

food_src = pd.read_excel(FOOD_FILE)
minimal_intake = pd.read_excel(MINIMAL_INTAKE_FILE)
stopwords = open("../data/stopwords.txt").read().splitlines()

app = flask.Flask(__name__)
app.config["DEBUG"] = True


# Helper method to calculate occurence
def calculate_occurence(query_tokens, name_tokens):
    occurence = 0
    for query_token in query_tokens:
        if query_token in name_tokens:
            occurence += 1

    return occurence / len(name_tokens)

# Helper method to retrieve foods by name


def get_food_nutrition_by_name(name):
    foods = food_src[food_src[MAIN_FOOD_DESCRIPTION].str.contains(
        name, na=False, case=False)]

    food_names = foods[MAIN_FOOD_DESCRIPTION]
    query_tokens = [word for word in word_tokenize(name) if word.isalnum()]

    percent_dict = {}
    mean = 0.0

    temp_list = []
    for index, food in foods.iterrows():
        name_tokens = [word for word in word_tokenize(
            food[MAIN_FOOD_DESCRIPTION]) if word.isalnum()]

        filtered_name_tokens = [
            word.lower() for word in name_tokens if not word.lower() in stopwords]

        if(len(filtered_name_tokens) == 0):
            temp_list.append(food[MAIN_FOOD_DESCRIPTION])

        occurence = calculate_occurence(query_tokens, filtered_name_tokens)
        percent_dict[index] = occurence

        mean += occurence

    print(temp_list)
    mean /= len(food_names) + 1
    accepted_idx = []
    for index, percent in percent_dict.items():
        if percent >= mean:
            accepted_idx.append(index)

    accepted_foods = food_src.iloc[accepted_idx]
    pruned_accepted_foods = accepted_foods.drop(
        [FOOD_CODE, MAIN_FOOD_DESCRIPTION], axis=1)
    mean = pruned_accepted_foods.mean()

    food = {FOOD_NAME: name}
    for nutrition, value in mean.items():
        if math.isnan(value):
            mean[nutrition] = 0.0

        food[nutrition] = float(mean[nutrition])

    return food


@app.route("/", methods=["GET"])
def home():
    return "<h1>FoodCountant</h1><p>An accountant, but for your food</p>"


@app.route("/get-lacking-nutrition")
def get_lacking_nutrition():
    food_diary = request.args.getlist("food_diary")
    gender = request.args.get("gender")
    age = int(request.args.get("age"))

    nutrition_sum = {}
    for day in food_diary:
        foods_in_day = day.split(",")
        for food in foods_in_day:
            nutrition = get_food_nutrition_by_name(food)

            for element in nutrition:
                if element is not FOOD_NAME:
                    nutrition_sum[element] = nutrition_sum.get(
                        element, 0.0) + nutrition[element]

    nutrition_mean = {}
    num_days = len(food_diary)
    for element in nutrition_sum:
        nutrition_mean[element] = nutrition_sum[element] / num_days

    required_nutrition_dataframe = minimal_intake[
        (minimal_intake[GENDER] == gender) &
        (minimal_intake[LOWER] <= age) &
        (minimal_intake[UPPER] >= age)]

    required_nutrition = {}
    for index, row in required_nutrition_dataframe.iterrows():
        required_nutrition = row.to_dict()

    lacking_nutrition = []
    for nutrition in nutrition_mean:
        consumed = nutrition_mean[nutrition]
        required = required_nutrition[nutrition]

        if consumed < required:
            lacking_nutrition.append(nutrition)

    return jsonify(lacking_nutrition)


@app.route("/get-foods-by-nutrients", methods=["GET"])
def get_foods_by_nutrients():
    nutrients = request.args.getlist("nutrients", None)

    result = food_src
    for nutrition in nutrients:
        result = result[result[nutrition] > 0]

    result.drop([FOOD_CODE, MAIN_FOOD_DESCRIPTION], axis=1)
    result.sort_values(nutrients, ascending=False, inplace=True)

    food_with_nutrients = result[MAIN_FOOD_DESCRIPTION].tolist()

    return jsonify(food_with_nutrients)


if __name__ == "__main__":
    app.run()
