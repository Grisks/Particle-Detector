import re, csv, ast
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import matplotlib.dates as mdates



particle_types_dict = {
    ".3": 1,
    ".5": 3,
    ".7": 5,
    "1.0": 7,
    "2.5": 9,
    "5.0": 11,
    "10.0": 13
}

while True:
    Log_name = "Logs/" + input("Please enter the log file name: ")
    try:
        open(Log_name).close()
    except:
        print("No Log file with that name")
    else:
        break
        

while True:
    try:
        particle_sizes = input("Please input particle size list: ").split(",")
        particle_sizes_str = str([a.strip() for a in particle_sizes]).removeprefix("[").removesuffix("]")
        particle_types = [particle_types_dict[a.strip()] for a in particle_sizes]
    except:
        print("Please enter particle sizes of the following: " + str(particle_types_dict.keys()))
    else:
        break
    
date_regex = r"_\d{8}"

start_date = re.search(date_regex,Log_name).group().removeprefix("_")
START_DAY = int(start_date[6:])
START_MONTH = int(start_date[4:6])
START_YEAR = int(start_date[2:4])
beginning_day_indexes = {str(START_MONTH) + '/' + str(START_DAY) + '/' + str(START_YEAR):0}
end_day_indexes = {}

with open(Log_name) as log:
    filelen = len(log.readlines())

with open(Log_name) as log:
    ValueArray = np.zeros((filelen-2,14),np.uint16)
    Times = np.zeros(filelen-2,dtype="datetime64[s]")
    values_pattern = r"Values: \[.*\]"
    value_pattern = r"\[.*\]"
    time_pattern = r"Time: [0-9:.]*"
    day = START_DAY

    i=0
    for line in log:
        timeMatch = re.search(time_pattern, line)
        valueMatch = re.search(values_pattern,line) 
        
        if valueMatch:
            timeString = str(START_MONTH) + '/' + str(day) + '/' + str(START_YEAR) + " " + timeMatch.group().removeprefix("Time: ").split(".")[0]
            date = datetime.strptime(timeString, "%m/%d/%y %H:%M:%S") 
            time = np.datetime64(date)
            Times[i] = time
            if date.strftime("%H:%M") == "23:59":
                end_day_indexes.update({str(START_MONTH) + '/' + str(day) + '/' + str(START_YEAR): i})
                day = day + 1
                beginning_day_indexes.update({str(START_MONTH) + '/' + str(day) + '/' + str(START_YEAR): i})
            valueString = valueMatch.group()
            values = ast.literal_eval(re.search(value_pattern, valueString).group())
            ValueArray[i] = values
            i += 1
    end_day_indexes.update({str(START_MONTH) + '/' + str(day) + '/' + str(START_YEAR):i})

with open(Log_name.removesuffix(".log")+".csv", 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Time",'0.3Hi', '0.3Lo', '0.5Hi', '0.5Lo', '0.7Hi', '0.7Lo', '1.0Hi', '1.0Lo', '2.5Hi', '2.5Lo', '5.0Hi', '5.0Lo', '10Hi', '10Lo'])
    for i in range(filelen-2):
        Values = ValueArray[i].tolist()
        Values.insert(0,str(Times[i]).replace('T', ' '))
        writer.writerow(Values)

pdf_file_name = 'data/'+Log_name.removeprefix("Logs/").removesuffix(".log") + "_" + particle_sizes_str + '_.pdf' 
with PdfPages(pdf_file_name) as pdf:
    # if LaTeX is not installed or error caught, change to `False`
    plt.rcParams['text.usetex'] = True
    for date in beginning_day_indexes:
        fig = plt.figure(figsize=(10,6))
        indexed_values = ValueArray.T
        for particle_type in particle_types:
            plt.plot(Times[beginning_day_indexes[date]: end_day_indexes[date]], indexed_values[particle_type][beginning_day_indexes[date]: end_day_indexes[date]])
        ax = fig.axes[0]
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        plt.title(date + " " + particle_sizes_str + " Particles")
        pdf.attach_note("")  # attach metadata (as pdf note) to page
        pdf.savefig()
        
    d = pdf.infodict()
    d['Title'] = 'Particle Detector Graphs from log file:' + Log_name
    d['Author'] = 'Graham Dirks'
    d['Subject'] = 'Graphs describing the particle count makeup and distribution over time in the clean room'
    d['Keywords'] = 'PdfPages multipage keywords author title subject'
    d['CreationDate'] = datetime(2024, 12, 11)
    d['ModDate'] = datetime.today()