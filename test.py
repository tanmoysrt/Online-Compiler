import json

data = json.load(open("./command.json","r"))

print(data["python3"]['build_command'].format("HI"))