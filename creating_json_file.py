import json
from datetime import datetime

eightballw_data = []
eightballl_data = []
nineballw_data = []
nineballl_data = []
frenchw_data = []
frenchl_data = []
snookerw_data = []
snookerl_data = []

date_time_score = datetime.now()
score_date = date_time_score.strftime("%x")

for i in range(0,5):
    eightballw_data.append([
        score_date,
        "Player 1", #winner
        0, #balls potted
        0, #turns taken
        0, #fouls
        0]) #overal score

def save_eightballw_data(data, filename="saves/eightballw_score.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    
save_eightballw_data(eightballw_data)


for i in range(0,5):
    eightballl_data.append([
        "Player 2", #looser
        0, #balls potted
        0, #turns taken
        0, #fouls
        0]) #overal score

def save_eightballl_data(data, filename="saves/eightballl_score.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    
save_eightballl_data(eightballl_data)


for i in range(0,5):
    nineballw_data.append([
        score_date,
        "Player 1",
        0,
        0,
        0,
        0])
         
def save_nineballw_data(data, filename="saves/nineballw_score.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

save_nineballw_data(nineballw_data)


for i in range(0,5):
    nineballl_data.append([
        "Player 2", #looser
        0, #balls potted
        0, #turns taken
        0, #fouls
        0]) #overal score
         
def save_nineballl_data(data, filename="nineballl_score.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

save_nineballl_data(nineballl_data)


for i in range(0,5):
    frenchw_data.append([
        score_date,
        "Player 1",
        300, #Turns
        5]) #Score
         
    
def save_frenchw_data(data, filename="saves/frenchw_score.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

save_frenchw_data(frenchw_data)


for i in range(0,5):
    frenchl_data.append([
        "Player 2",
        300, #Turns
        5]) #Score
         
    
def save_frenchl_data(data, filename="saves/frenchl_score.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

save_frenchl_data(frenchl_data)


for i in range(0,5):
    snookerw_data.append([
        score_date,
        "Player 1",
        0, #Balls Potted
        0, #Turns
        0, #Fouls
        0]) #Score

def save_snookerw_data(data, filename="saves/snookerw_score.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

save_snookerw_data(snookerw_data)


for i in range(0,5):
    snookerl_data.append([
        "Player 2",
        0, #Balls Potted
        0, #Turns
        0, #Fouls
        0]) #Score

def save_snookerl_data(data, filename="saves/snookerl_score.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

save_snookerl_data(snookerl_data)

options_data = ['enabled', 'green', 'player 1', 'player 2']
def options_save(data, filename ="saves/options_data.json"):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

options_save(options_data)

 