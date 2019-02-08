import random

# Insert emojis for slack bot depending on food type
def addEmojis(food):
    # Check if closed
    if food[:5].lower() == 'lokað':
        return ':no_entry_sign: ' + food

    # Check for vegan, replace v for :leaves:
    if food.lower()[-2:] == " v":
        food = food[:-2] + ' :leaves:'
    if " v " in food.lower():   
        food = food.replace(" v ", " :leaves: ")

    anyFood = [':shallow_pan_of_food:', ':canned_food:', ':ok_hand:', ':pray:', ':pineapple:', 
        ':eggplant:', ':potato:', ':mushroom:', ':bread:', ':pretzel:', ':broccoli:', ':curry:', ':chopsticks:']
    anyMeat = [':cut_of_meat:', ':meat_on_bone:', ':poultry_leg:']
    anyChic = [':hatched_chick:', ':hatching_chick:', ':chicken:', ':baby_chick:']
    fish = ['fiskur', 'fisk', 'ýsa', 'þorsk', 'bleikja', 'lax', 'síld', 'loðna', 'langa',
        'urriði', 'skötuselur']
    emoji = ''

    if 'súpa' in food.lower():
        emoji = ':stew:'
    elif any(x in food.lower() for x in ['hamborg', 'borgar', 'hamburg']):
        emoji = ':hamburger:'
    elif any(x in food.lower() for x in fish):
        emoji = ':fish:'
    elif 'burrito' in food.lower() or 'vefja' in food.lower():
        emoji = ':burrito:'
    elif 'taco' in food.lower():
        emoji = ':taco:'
    elif 'píta' in food.lower():
        emoji = ':stuffed_flatbread:'
    elif 'satay' in food.lower():
        emoji = ':oden:'
    elif any(x in food.lower() for x in ['karr', 'curr', 'dhal', 'dal', 'falafel', 'pottr']):
        emoji = ':curry:'
    elif 'paella' in food.lower() or 'pælla' in food.lower():
        emoji = ':shallow_pan_of_food:'
    elif 'núðl' in food.lower():
        emoji = ':ramen:'
    elif 'samosa' in food.lower():
        emoji = ':dumpling:'
    elif any(x in food.lower() for x in ['pasta', 'spagett', 'tagliat']):
        emoji = ':spaghetti:'
    elif 'lasagn' in food.lower() or 'pie' in food.lower():
        emoji = ':pie:'
    elif 'grasker' in food.lower():
        emoji = ':jack_o_lantern:'
    elif 'humar' in food.lower() or 'rækj' in food.lower():
        emoji = ':shrimp:'
    elif 'lamb' in food.lower():
        emoji = ':sheep:'
    elif any(x in food.lower() for x in ['kjúkl', 'kalkú']):
        emoji = random.choice(anyChic)
    elif any(x in food.lower() for x in ['naut', 'carne', 'hakk']):
        emoji = ':cow:'
    elif any(x in food.lower() for x in ['grís', 'puru', 'skinka', 'pork', 'svín']):
        emoji = ':pig:'
    elif 'bjúga' in food.lower():
        emoji = ':horse:'
    elif 'steak' in food.lower():
        emoji = ':cut_of_meat:'
    elif 'buff' in food.lower():
        emoji = ':pancakes:'
    elif any(x in food.lower() for x in ['chili', 'chilli']):
        emoji = ':hot_pepper:'
    elif 'hnetu' in food.lower():
        emoji = ':peanuts:'
    elif 'kartöf' in food.lower():
        emoji = ':potato:'
    elif 'hrísgrj' in food.lower():
        emoji = ':rice:'
    elif 'tómat' in food.lower():
        emoji = ':tomato:'
    elif 'svepp' in food.lower():
        emoji = ':mushroom:'
    elif any(x in food.lower() for x in ['spínat', 'brokkol', 'kál']):
        emoji = ':broccoli:'
    elif any(x in food.lower() for x in ['græn', 'taboul']):
        emoji = ':green_salad:'
    elif any(x in food.lower() for x in ['mais', 'maís', 'majs']):
        emoji = ':corn:'
    elif 'steik' in food.lower():
        emoji = ':fire:'
    else:
        emoji = random.choice(anyFood)
    return emoji + ' ' + food