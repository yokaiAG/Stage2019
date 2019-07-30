# coding: utf-8

links = set()

for file_path in {"../Datasets/russian_adjList_full.txt", "../Datasets/russian_adjList_new.txt", "../Datasets/russian_adjList_new2.txt", "../Datasets/russian_adjList.txt"}:
    print(file_path)
    for line in open(file_path):
        line = [int(x) for x in line.split()]
        links.add((line[0], line[1]))

with open("../Datasets/russian_adjList_FINAL.txt", 'w') as out:
    for (x,y) in links:
        out.write("{} {}\n".format(x,y))
