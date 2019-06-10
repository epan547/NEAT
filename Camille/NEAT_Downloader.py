"""
Written By Siddarth Garimella
Source Code can be found here: https://github.com/gsidsid/neat

Edits made by Camille Xue
"""
from bs4 import BeautifulSoup
import urllib.request as urllib2
import requests
import subprocess
import threading
import re
import os

NEAT_vol_1 = 'https://sbnarchive.psi.edu/pds3/neat/geodss/data/'
NEAT_vol_1_folder = "geodss"
NEAT_vol_2 = 'https://sbnarchive.psi.edu/pds3/neat/tricam/data/'
NEAT_vol_2_folder = "tricam"
NEAT_vol_3 = 'https://sbnarchive.psi.edu/pds3/neat/tricam2/data/'
NEAT_vol_3_folder = "tricam2"


def pullVolumeData(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    links = [
        url +
        '/' +
        node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]
    return links[5:-2]


def getRecordsFromVolumeData(data, _idx):
    if isinstance(_idx, int):
        return [data[_idx]]
    else:
        x = []
        for i in _idx:
            x.append(data[i])
        return x


def read_url(url, rL):
    url = url.replace(" ", "%20")
    req = urllib2.Request(url)
    a = urllib2.urlopen(req).read()
    soup = BeautifulSoup(a, 'html.parser')
    x = (soup.find_all('a'))
    for i in x:
        file_name = i.extract().get_text()
        url_new = url + file_name
        url_new = url_new.replace(" ", "%20")
        if(file_name[-1] == '/' and file_name[0] != '.'):
            read_url(url_new, rL)
        rL.append(url_new)


def getRecordID(record):
    return record.split('/')[-2]


def fetchRecord(record, verbose=False):
    file_idx = 0
    recordData = []
    read_url(record, recordData)
    # print(record)
    print("Fetching record " + getRecordID(record) + "...")
    print("wget -r -nH -nc --cut-dirs=2 --no-parent --reject=\"index.html*\" " + str(record))
    os.system(
        "wget -r -nH -nc --cut-dirs=2 --no-parent --reject=\"index.html*\" " +
        str(record))
    if(verbose):
        print("Completed fetching record " + getRecordID(record) + "\r")
    else:
        print("Completed fetching record " + getRecordID(record))
    # print("Unpacking...")
    # subprocess.call("sh f.sh", shell=True)
    # print("Done!")


def fetchRecords(data):
    for record in data:
        t = threading.Thread(target=fetchRecord, args=(record, False))
        t.start()


NEAT_vol_1_data = pullVolumeData(NEAT_vol_1)
for i in range(0, len(NEAT_vol_1_data)):
    palomar = getRecordsFromVolumeData(NEAT_vol_1_data, i)
    fetchRecords(palomar)

NEAT_vol_2_data = pullVolumeData(NEAT_vol_2)
palomar = getRecordsFromVolumeData(NEAT_vol_2_data, 10)
fetchRecords(palomar)
