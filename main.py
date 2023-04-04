import configparser

import vk
import matplotlib.pyplot as plt
import networkx as nx
from datetime import datetime
import time


def write_in_file_ids(dict):
    open('ids_checked.txt', 'w').close()
    file = open('ids_checked.txt', 'w')
    for key in dict:
        file.write(str(key) + " ")
        file.write(str(dict[key]).replace('[', '').replace(']', '').replace(',', '').replace('"', '').replace('\'', ''))
        file.write('\n')
    file.close()


class Parser:
    def deep_friends(user_id, deep, ids_checked):
        time.sleep(1)
        # Получаем информацию о текущем пользователе
        info = api.execute.userInfoAndFriends(targets=[user_id], v=VERSION)
        person = info[0]
        if 'deactivated' not in person[0] \
                and bool(person[0]['can_access_closed']) is True:
            person_name = person[0]['first_name']
            person_last_name = person[0]['last_name']
            person_id = str(person[0]['id'])
            friends = info[1]
            friends_info = api.users.get(user_ids=','.join([str(i) for i in friends['items']]), v=VERSION)
            # Пишем друзей в файл
            f = open('edgelist.txt', 'a', encoding='utf-8')
            for friend in friends_info:
                if 'deactivated' not in friend:
                    friend_name = str(friend['first_name']).replace(':', ' ')
                    friend_last_name = str(friend['last_name']).replace(':', ' ')
                    if len(str(friend_last_name)) == 0:
                        friend_last_name = " "
                    friend_id = str(friend['id'])
                    if friend_id not in ids_checked.keys():
                        node = '{}/{}/{}:{}/{}/{}:'.format(person_name, person_last_name, person_id, friend_name,
                                                           friend_last_name,
                                                           friend_id) + '{}\n'
                        f.write(node)
            f.close()
        else:
            return
        # Если глубина не равна 0 - вызываем функцию для всех друзей текущего пользователя
        if deep == 0:
            return
        else:
            for friend in friends['items']:
                if str(friend) not in ids_checked.keys():
                    ids_checked.update({friend: [deep - 1]})
                    write_in_file_ids(ids_checked)
                    Parser.deep_friends(friend, deep - 1, ids_checked)
                elif str(deep - 1) not in ids_checked[str(friend)]:
                    ids_checked[str(friend)].append(deep - 1)
                    write_in_file_ids(ids_checked)
                    Parser.deep_friends(friend, deep - 1, ids_checked)


ids_checked = {}
with open('ids_checked.txt') as file:
    while line := file.readline().rstrip():
        data = line.split(' ')
        key = data.pop(0)
        values = data
        ids_checked.update({key: values})
print(ids_checked)

config = configparser.ConfigParser()
config.read("config.ini")

VERSION = config["vk"]["api_v"]
user_id = config["vk"]["user_id"]
deep = int(config["vk"]["deep"])
access_token = config["vk"]["access_token"]

api = vk.API(access_token=access_token)
print(datetime.now())
Parser.deep_friends(user_id, deep, ids_checked)
print(datetime.now())

ids_checked = []
with open('edgelist.txt', 'r', encoding="utf8") as file:
    while line := file.readline().rstrip():
        ids_checked.append(line)
print(len(ids_checked))
unic_strings = set(ids_checked)
print(len(unic_strings))

open('edgelist.txt', 'w').close()
with open('edgelist.txt', 'a', encoding="utf8") as file:
    for i, val in enumerate(unic_strings):
        # file.write(str(val).replace('(', '').replace(')', '').replace("'", '') + '\n')
        file.write(str(val).replace('(', '').replace(')', '').replace("'", '').replace(' ', '') + '\n')

# чтение графа из файла
# # отрисовка графа в .png изображение

G = nx.Graph()
G = nx.read_edgelist('edgelist.txt', delimiter=':')
plt.figure(figsize=(24,24))
nx.draw(G, pos=nx.spring_layout(G))
pagerank = nx.pagerank(G)
f = open('pagerank.txt', 'a', encoding='utf-8')
for i in pagerank:
    f.write(str(i) + " " + str(pagerank[i]) + '\n')
f.close()
plt.savefig("plot.png", dpi=1000)
pagerank_default = {}
with open('pagerank.txt', 'r', encoding='utf8') as file:
    while line := file.readline().rstrip():
        pagerank_default.update({line.split(' ')[0]: line.split(' ')[1]})
sorted_pagerank = {}
sorted_keys = sorted(pagerank_default, key=pagerank_default.get, reverse=True)
for k in sorted_keys:
    sorted_pagerank[k] = pagerank_default[k]
with open('pagerank_sorted.txt', 'a', encoding='utf8') as file:
    for j in sorted_pagerank:
        file.write(str(j) + " " + str(sorted_pagerank[j]) + '\n')
