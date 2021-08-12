import flask
import pandas as pd

from flask import request
from nltk.tokenize import word_tokenize

FILE = "../data/small.csv"
MAIN_FOOD_DESCRIPTION = "Main food description"

food_src = pd.read_csv(FILE)
useless_data = ["Food code", "WWEIA Category number",
                "WWEIA Category description"]
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


@app.route("/", methods=["GET"])
def home():
    return "<h1>FoodCountant</h1><p>An accountant, but for your food</p>"


@app.route("/get-food-by-name", methods=["GET"])
def get_food_by_name():
    name = request.args.get("name", None)

    foods = food_src[food_src[MAIN_FOOD_DESCRIPTION].str.contains(
        name, na=False, case=False)]

    food_names = foods[MAIN_FOOD_DESCRIPTION]
    query_tokens = [word for word in word_tokenize(name) if word.isalnum()]

    percent_dict = {}
    mean = 0.0
    for idx in range(0, len(food_names)):
        name_tokens = [word for word in word_tokenize(
            food_names[idx]) if word.isalnum()]

        filtered_name_tokens = [
            word.lower() for word in name_tokens if not word.lower() in stopwords]

        occurence = calculate_occurence(query_tokens, filtered_name_tokens)
        percent_dict[idx] = occurence

        mean += occurence

    mean /= len(food_names) + 1
    accepted_idx = []
    for idx, percent in percent_dict.items():
        if percent >= mean:
            accepted_idx.append(idx)

    accepted_foods = food_src.iloc[accepted_idx]
    pruned_accepted_foods = accepted_foods.drop(
        useless_data + [MAIN_FOOD_DESCRIPTION], axis=1)
    mean = pruned_accepted_foods.mean()

    food = {"food_name": name}
    for key in mean.keys():
        food[key] = mean[key]

    return food


@app.route("/get-foods-by-nutrients", methods=["GET"])
def get_foods_by_nutrients():
    nutrient_name = request.args.get("nutrient_name", None)
    nutrient_value = float(request.args.get("nutrient_value", None))

    result = food_src[food_src[nutrient_name] >=
                      nutrient_value].drop(useless_data, axis=1)

    return result.to_dict()


if __name__ == "__main__":
    app.run()
