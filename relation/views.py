from django.shortcuts import render
from django.db import connection
from django.conf import settings
import json


# Create your views here.
def index(request):
    context = {}
    context['hello'] = 'Hello World!'
    tableClass = MysqlTableMap()
    tableMap = tableClass.getTableMap()
    tableData = {}
    for i in tableMap:
        tableData[i] = tableClass.getTableCloumns(i)
    # 对应关系写入文件
    tableClass.writeJson(tableData, tableClass.origin_json_url)
    # 生成echarts对应json文件
    tableClass.covertToEchart()

    return render(request, 'relation/map.html', context)


class MysqlTableMap:
    def __init__(self):
        self.tableMap = {}
        self.origin_json_url = './relation/templates/relation/origin_data.json'
        self.echart_json_url = './relation/static/echart_data.json'

    def getTableMap(self):
        cursor = connection.cursor()
        cursor.execute("show tables;")
        tables = cursor.fetchall()
        res = {}
        for table in tables:
            res[table[0]] = table[0]
        self.tableMap = res
        return res

    def getTableCloumns(self, tablename):
        cursor = connection.cursor()
        cursor.execute("show full columns from " + tablename)
        cloumns = cursor.fetchall()
        res, relation = {}, {}
        for clo in cloumns:
            title = clo[0]
            des = clo[8]
            rel = self.matchRelationTable(tablename, title)
            if rel != "":
                relation[title] = rel
        res['relation'] = relation
        res['table'] = tablename
        # print(res)
        return res

    def matchRelationTable(self, tablename, name):
        l = name.split('_')
        newname = ''

        if l[-1] == 'id':
            newl = l[:-1]
            newname = "_".join(newl)
        else:
            return ''
        for i in [newname, newname + 's']:
            i = settings.TABLEPREFIX + i
            # print(i)
            if self.tableMap.get(i):
                # print(self.tableMap.get(i))
                return self.tableMap.get(i)
        # print(name + ' not found')
        return ''

    def covertToEchart(self):
        jsonData = self.readJson(self.origin_json_url)
        nodes, links, categories = [], [], []
        x , y = -500, 500
        counts = 0
        for i in jsonData:
            tempJData = jsonData[i]
            x = x + 400
            nodes.append({
                "id": tempJData["table"],
                "name": tempJData["table"],
                "symbolSize": 5,
                "x": x,
                "y": y,
                "value": tempJData["table"],
                "category": tempJData["table"],
            })
            yu = self.mod(counts, 4)
            if yu == 0:
                y = y + 400
            elif yu == 1:
                y = y - 400
            elif yu == 2:
                y = y - 400
            elif yu == 3:
                y = y + 400


            for link in tempJData['relation']:
                print(link)
                links.append({
                    "source": tempJData["table"],
                    "target": tempJData['relation'][link],
                })

            categories.append({
                "name": tempJData["table"]
            })
            counts = counts + 1
            # print(jsonData[i])

        res = {}
        res["nodes"] = nodes
        res["links"] = links
        res["categories"] = categories
        self.writeJson(res, self.echart_json_url, True)

    def mod(self, a, b):
        c = a // b
        r = a - c * b
        return r

    def writeJson(self, data, filename, format=False):
        with open(filename, 'w') as file_obj:
            if format:
                json.dump(data, file_obj, indent=4)
            else:
                json.dump(data, file_obj)

    def readJson(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                while True:
                    line = f.readline()
                    # print(line)
                    if line:
                        r = json.loads(line)
                        # print(r)
                        return r
                    else:
                        break
            except:
                f.close()
