import flask
import pandas as pd

from flask import request

FILE = "../data/small.csv"

food_src = pd.read_csv(FILE)
useless_data = ["Food code", "WWEIA Category number",
                "WWEIA Category description"]

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route("/", methods=["GET"])
def home():
    return "<h1>FoodCountant</h1><p>An accountant, but for your food</p>"


@app.route("/get-food-by-name", methods=["GET"])
def get_food_by_name():
    name = request.args.get("name", None)

    foods = food_src[food_src["Main food description"].str.contains(
        name, na=False, case=False)]

    pruned_foods = foods.drop([useless_data, "Main food description"], axis=1)
    mean = pruned_foods.mean()

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
