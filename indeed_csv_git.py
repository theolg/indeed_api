#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET

from indeed import IndeedClient

import time, csv, codecs, cStringIO

#UnicodeWriter is a workaround to use the csv module with non-ASCII characters in Python 2. See http://bit.ly/1WNfbXY
class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def generate_job_list(params,publisher_id):
    """
    Returns list of jobs that match search criteria
    """
    job_list = []
    #since we initiated params['start'] at 0
    total_results = 1     
    while int(params['start']) < total_results:
        client = IndeedClient(publisher = publisher_id)
        search_response = client.search(**params)
        root = ET.fromstring(search_response)
        params['start']  = str(int(params['start'])+25) 
        total_results = int(root.find('totalresults').text)         
        for job in root.iter('result'):
            jobtitle = job.find('jobtitle').text 
            company = job.find('company').text
            city = job.find('city').text
            #state = job.find('state').text
            #country = job.find('country').text
            date = job.find('date').text
            snippet = job.find('snippet').text
            sponsored = job.find('sponsored').text
            url = job.find('url').text
            job = (unicode(jobtitle),unicode(company),unicode(city),unicode(date)[5:16].replace(" ","-"),unicode(sponsored), unicode(url))
            if job not in job_list:
                job_list.append(job)         
            
    job_list.insert(0,(unicode("jobtitle"),unicode("company"),unicode("city"),unicode("date"),unicode("sponsored"), unicode("url"))) #add header    
    return job_list

def csv_file_creator(path, list_of_jobs):
    """
    Takes a list of jobs and creates a csv file 
    """
    with open(path, "wb") as out_file:
        writer = UnicodeWriter(out_file, delimiter=',')
        for row in list_of_jobs:
            writer.writerow(row)

if __name__ == "__main__":
    
    QUERY = ""
    LOCATION = ""
    COUNTRY  = "" 
    LIMIT = "" 
    USERIP = ""
    USERAGENT = ""
    DAYS = ""
    FORMAT = "xml"
    RAW = "True"   
    PUBLISHER_ID = "" 

    params = {
        'q' : QUERY,
        'l' : LOCATION,
        'co' : COUNTRY,
        'start': "0",
        'limit' : LIMIT,
        'userip' : USERIP,
        'useragent' : USERAGENT,
        'fromage' : DAYS,
        'format' : FORMAT,
        'raw' : RAW
        }

    job_list = generate_job_list(params, PUBLISHER_ID)
    csv_filename = "indeed_search_" + time.strftime("%d_%m_%Y_%H_%M_%S", time.localtime()) + ".csv" #generates filename
    csv_file_creator(csv_filename, job_list)     
