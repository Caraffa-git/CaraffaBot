import aiohttp
import random

randomapi_animals = {
    "fox": "https://some-random-api.ml/animal/fox",
    "red_panda": "https://some-random-api.ml/animal/red_panda",
    "koala": "https://some-random-api.ml/animal/koala",
    "bird": "https://some-random-api.ml/animal/birb",
    "raccoon": "https://some-random-api.ml/animal/raccoon",
    "kangaroo": "https://some-random-api.ml/animal/kangaroo",
    "cat": "https://some-random-api.ml/animal/cat",
    "dog": "https://some-random-api.ml/animal/dog"
}

async def get_animal_image(session: aiohttp.ClientSession, arg = None):
    if arg == None:
        name, url = random.choice(list(randomapi_animals.items()))
        async with session.get(url) as request:
            json = await request.json()
    elif arg in randomapi_animals:
            async with session.get(randomapi_animals[arg]) as request:
                    json = await request.json()
    else: raise KeyError
    
    return json

    