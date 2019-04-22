#!/usr/bin/env python
import csv
import pandas as pd
import sys
import numpy as np
import glob
from sklearn.cluster import KMeans
from datetime import datetime
from itertools import zip_longest

"""@package docstring
Srautiniu duomenu analizes irankio dokumentacija.
"""


def get_time(row):

    return [x.strip() for x in row[0].split(';')][0]


def get_all_csv_files():
    """
    Gaunami visi '.csv' failai esantys 'duomenys' direktorijoje

    :return: Rastu failu pavadinimu masyvas
    """

    csvFiles = [f for f in glob.glob("duomenys/*.csv")]
    return csvFiles


def get_data_filename():
    """
    Leidzia pasirinkti viena is galimu duomenu failu ir grazina pasirinkto failo pavadinima

    :return: Pasirinkto failo pavadinimas
    """

    allCsvFiles = get_all_csv_files()
    fileCount = len(allCsvFiles)

    if fileCount == 0:
        print(u"Nerastas CSV failas. Prasome įkelti duomenų failą CSV formatu į šios programos aplankalą.")
        return None
    else:
        if fileCount == 1:
            print("Rastas tik vienas CSV failas: " + allCsvFiles[0])
            input(u"Spauskite Enter norėdami jį naudoti. Norint išeiti spauskite CTRL+C.")
            return allCsvFiles[0]
        else:
            if fileCount > 9:
                print(u"Rasti " + str(fileCount) + " failų.")
            else:
                print(u"Rasti " + str(fileCount) + " failai.")
            for idx, csvFile in enumerate(allCsvFiles):
                print(str(idx) + ") " + csvFile)
            fileNumber = input(u"Įrašykite norimo nagrinėti failo numerį: ")
            return allCsvFiles[int(fileNumber)]


def get_data(row):

    list = [x.strip() for x in row[0].split(';')]
    list.pop(0)
    return list


def manipulate_data(time, list):

    values = avg_values(list)
    result = [time] + values
    return result


def check_float_to_int(value):
    if value == 1 or value == 0:
        return int(value)
    return value


def avg_values(values):
    suma = 0
    count = len(values[0])
    index = 0
    result = []

    for x in range(0, count):
        for value in values:
            if value[x]:
                index = index + 1
                suma = suma + float(value[x])

        if suma != 0 and index != 1:
            suma = suma / index
        result.append(check_float_to_int(suma))
        index = 0
        suma = 0
    return result


def get_file_name():
    file_name = input(u"Išvedamo failo pavadinimas: ")
    return "rezultatai/" + file_name


def write_to_file(list, file_name):
    """
    Iraso duomenis i faila
    :param list: duomenys
    :param file_name: rezultatu failo pavadinimas
    """

    with open(file_name + '_1dalis.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in list:
            writer.writerow(row)
    file.close()


# get start time, end time and headers
def get_info(reader, file):
    for reverse_row in reversed(list(reader)):
        last_line = reverse_row
        break

    file.seek(0)

    for idx, row in enumerate(reader):
        if idx == 0:
            header = row
            continue
        first_line = row
        break

    first_time = get_time(first_line)
    last_time = get_time(last_line)

    print(u"Duomenys skaičiuojami nuo: " + first_time)
    print("iki: " + last_time)

    result = []

    result.append(first_time)
    result.append(last_time)
    result.append(header)

    return result


def get_dates():
    """
    Gaunami datos parametrai pradinio duomenu failo paruosimui
    :return: Masyvas ['pradzios_data', 'pabaigos_data']
    """

    start = input(u"Įrašykite nuo kada pradėti analizuoti: ")
    end = input(u"Įrašykite iki kada norite analizuoti: ")
    print("Analizuojama nuo " + start + " iki " + end)

    return [start, end]


def get_parameters(params):
    """
    Gaunami paramentrai pagal kurios bus analizuojami failai

    :return: Pasirinktu parametru skaitiniai atitikmenys
    """

    headers = get_data(params)
    print(u"Pasirinkite pagal kuriuos parametrus norite analizuoti: \n")

    for index, param in enumerate(headers):
        print(u"Pasirinkite " + str(index) + " jei norite analizuoti pagal '" + param + "' požymį.")
    numbers = input("Įrašykite skaičiu(s) su tarpais: ")

    return numbers.split()


def filter_data(row, filters):
    result = []
    for index, param in enumerate(row):
        for f in filters:
            if int(f) == index:
                result.append(param)

    return result


def check_time(time_window, time):
    return time_window[0] <= time and time_window[1] >= time


# TODO padaryti filtru tikrinima
def check_keys(dict, keys):
    for key in keys:
        if key in dict:
            print("yra")
        else:
            print("nera")


def do_discretization(input_file_path, discretization_interval, output_file_path, columns, ascending=True):
    """
    Ivykdoma duomenu diskretizacija
    """

    # =========== 2 Task (discretization) ==============
    df = pd.read_csv(input_file_path, header=None,
                     # usecols=columns,
                     index_col=0)
    df[0] = pd.to_datetime(df.index, format='%Y.%m.%d %H:%M:%S')
    data = df.groupby(pd.Grouper(key=0, freq=discretization_interval)).mean().dropna()

    index = 0
    if 7 in columns:
        for sk in data[data.columns[-1]]:
            val = sk
            if val > 0.5:
                val = 1.0
            else:
                val = 0.0
            data[data.columns[-1]][index] = val
            index += 1


    data.to_csv(output_file_path, date_format='%Y.%m.%d %H:%M:%S')


    # =========== 3 Task (cutting) ==============

    # data = data.sort_values(data.columns[-1], ascending=ascending)


    # data_0 = data.loc[data[data.columns[-1]] == 0.0]
    # data_1 = data.loc[data[data.columns[-1]] == 1.0]
    #
    # output_path_prefix = output_file_path.split('.')[0]
    #
    # data_0.to_csv(output_path_prefix+'_3dalis_0.csv', date_format='%Y.%m.%d %H:%M:%S')
    # data_1.to_csv(output_path_prefix+'_3dalis_1.csv', date_format='%Y.%m.%d %H:%M:%S')


while True:
    dataFileName = get_data_filename()
    if dataFileName != None:
        break
    else:
        input(u"Įkėlę failą spauskite 'Enter'. Jei norite išeiti - spauskite CTRL+C.")

file = open(dataFileName, 'r')

with file as csvFile:
    reader = csv.reader(csvFile)
    file_name = get_file_name()
    info = get_info(reader, file)
    dates = get_dates()

    filters = get_parameters(info[2])

    i = -1
    this_second = 1
    previous_second = 0

    modified_matrix = []
    temp = []

    for idx, row in enumerate(reader):
        if idx == 0:
            continue

        time = get_time(row)
        if not check_time(dates, time):
            continue

        if time != this_second:
            previous_second = this_second
            this_second = time
            i = i + 1

            if i != 0:
                good_data = manipulate_data(previous_second, temp)
                modified_matrix.append(good_data)
                temp = []
            # break

        filtered_data = filter_data(get_data(row), filters)
        temp.append(filtered_data)

    write_to_file(modified_matrix, file_name)

    df = pd.DataFrame.from_records(modified_matrix)
    columns = [int(col) + 1 for col in filters]
    columns.insert(0, 0)

    while True:
        time_interval = input(u"Įveskite diskretizavimo laiko intervalą (pvz.'1s' t.y. viena sekundė): ")
        do_discretization(file_name + '_1dalis.csv', time_interval, file_name + '_diskretizuoti_' + time_interval + '.csv',
                          columns)

        do_repeat = input(
            'Ar norite kartoti diskretizavimą su kitu intervalu (y/n)? (įveskite \'y\' jeigu norite arba \'n\' jeigu '
            'nenorite): ')

        if do_repeat.lower() != 'y':
            break

    while True:

        trueTime = datetime.strptime(dates[1], '%Y.%m.%d %H:%M:%S')- datetime.strptime(dates[0], '%Y.%m.%d %H:%M:%S')
        trueMinutes = trueTime.total_seconds() / 60

        inputFileObject = []

        with open(str(file_name + '_1dalis.csv'), 'r') as fileToRead:
            reader = csv.reader(fileToRead)
            next(fileToRead)
            for row in reader:
                inputFileObject.append(row)

        minutesInterval = input(u"Po kelias minutes karpyti darbo rėžimo srautą? ")

        inputFileObject = [e for e in inputFileObject if e]

        transformedTimeArrayOfData = []

        for arrayOfData in inputFileObject:
            datetime_object = datetime.strptime(arrayOfData[0], '%Y.%m.%d %H:%M:%S')
            arrayOfData[0] = datetime_object
            transformedTimeArrayOfData.append(arrayOfData)

        timeElement = transformedTimeArrayOfData[0][0].minute + int(minutesInterval)

        i = 0
        groupedData = [[] for _ in range(200)]

        for oneLineInArray in transformedTimeArrayOfData:
            if oneLineInArray[0].minute < timeElement:
                oneLineInArray[0] = oneLineInArray[0].strftime('%Y%m%d%H%M%S')
                groupedData[i].append(oneLineInArray)
            else:
                i = i + 1
                timeElement = timeElement + int(minutesInterval)

        groupedData = [e for e in groupedData if e]

        clustersCount = input(u'Įveskite į kiek klasterizuotų grupių norite suskirstyti duomenis, kurie dabar yra sugrupuoti po: ' + minutesInterval + ' minutes: ')

        grouping_attribute = input(u"Pagal kurį atributą grupuoti duomenis, pasirinkite nuo 1 iki " + str(len(inputFileObject[0])-1) + ":")
        headerName = int(grouping_attribute)

        headers = get_data(info[2])
        attribute = headers[headerName].replace(" ", "_")

        data = [[] for _ in range(200)]

        x = 0
        y = 0

        for OneGroup in groupedData:
            clusteredCenters = []

            a = np.array(OneGroup)

            kmeans = KMeans(n_clusters=int(clustersCount))

            kmeans.fit(a)

            clusteredCenters.append(kmeans.cluster_centers_[:, int(grouping_attribute)])

            sortedClusterValues = sorted(clusteredCenters[0])

            lastCluster = 0

            for index, clusterValue in enumerate(sortedClusterValues):

                for oneRow in OneGroup:

                    if (float(oneRow[int(grouping_attribute)]) < clusterValue and float(
                            oneRow[int(grouping_attribute)]) > lastCluster):

                        data[x].append(oneRow)

                    elif (index == len(sortedClusterValues) - 1):

                        if (float(oneRow[int(grouping_attribute)]) > clusterValue):
                            data[x].append(oneRow)

                groupedDataStats = [[] for _ in range(100)]
                i = 0

                for separatedGroup in data:
                    if separatedGroup is None:
                        continue
                    elif not separatedGroup and isinstance(separatedGroup, list):
                        continue
                    elif not isinstance(separatedGroup, list):
                        continue

                    groupedDataStats[i].append(np.average(np.array(separatedGroup).astype(np.float), axis=0))

                    groupedDataStats[i].append(np.min(np.array(separatedGroup).astype(np.float), axis=0))

                    groupedDataStats[i].append(np.max(np.array(separatedGroup).astype(np.float), axis=0))

                    groupedDataStats[i].append(np.percentile(np.array(separatedGroup).astype(np.float), 25, axis=0))

                    groupedDataStats[i].append(np.percentile(np.array(separatedGroup).astype(np.float), 50, axis=0))

                    groupedDataStats[i].append(np.percentile(np.array(separatedGroup).astype(np.float), 75, axis=0))

                    groupedDataStats[i].append(np.var(np.array(separatedGroup).astype(np.float), axis=0))

                    i += 1
                lastCluster = clusterValue

                x += 1

        trueGroups = trueMinutes / float(minutesInterval)

        with open(file_name+'_klasterizuoti_duomenys_'+minutesInterval+'min_'+clustersCount + 'grup.csv', "w",
                  newline='') as fileToWrite:
            wr = csv.writer(fileToWrite)
            wr.writerow(("1. "+minutesInterval+" minuciu grupe", " ", " ", " ", " ", " ", " "))
            wr.writerow(("Vid", "Min", "Max", "Q1", "Mediana", "Q3", "Dispersija"))
            z = 2
            for count, element in enumerate(groupedDataStats, 1):
                if element is None:
                    continue
                elif not element and isinstance(element, list):
                    continue
                elif not isinstance(element, list):
                    continue

                zipped_stats = list(map(list, zip_longest(*element)))

                wr.writerows(zipped_stats)

                if count % int(clustersCount) != 0:
                    wr.writerow((" ", " ", " ", " ", " ", " ", " "))
                if count % int(clustersCount) == 0:
                    if trueMinutes > count:
                        wr.writerow((str(z) +". "+minutesInterval+" minuciu grupe", " ", " " " ", " ", " "))
                        wr.writerow(("Vid", "Min", "Max", "Q1", "Mediana", "Q3", "Dispersija"))
                    z += 1


        fileToWrite.close()

        do_repeat = input(
            'Ar norite kartoti duomenų analizavimą su kitais parametrais? (įveskite \'y\' jeigu norite arba \'n\' jeigu '
            'nenorite): ')

        if do_repeat.lower() != 'y':
            break
