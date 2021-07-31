import pandas as pd

file = "../data/small.csv"

# csv = pd.read_csv("../data/small.csv")

# protein_more_than = csv[csv["Protein (g)"] > 3.2]
# print(protein_more_than)

food_src = pd.read_csv(file)

useless_data = ['Food code', 'Main food description',
                'WWEIA Category number', 'WWEIA Category description']


def get_food_by_name(name):
    foods = food_src[food_src["Main food description"].str.contains(
        name, na=False, case=False)]

    pruned_foods = foods.drop(useless_data, axis=1)
    mean = pruned_foods.mean()

    food = {"food_name": name}
    for key in mean.keys():
        food[key] = mean[key]

    return food


def get_foods_by_nutrients(nutrient_name, nutrient_value):
    return food_src[food_src[nutrient_name] >= nutrient_value]


# get_food_by_name('milk')
# tmp = get_foods_by_nutrients('Protein (g)', 3.3)
# print(str(tmp))
