import multiprocessing as mp
from pickle_cleaning import *
from time import ctime

if __name__ == '__main__':
    jobs = []
    print(ctime())
    Date_file = ['201503','201504','201505','201506','201507','201508','201509','201510','201511','201512'] #YearMonth needed
    for i in range(len(Date_file)):
        p = mp.Process(target=pickle_cleaning, args=('arg'+Date_file[i]+'.csv','arg'+Date_file[i]+'data.p'))
        jobs.append(p)
        p.start()
    print(ctime()+'end')
