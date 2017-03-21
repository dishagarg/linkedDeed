"""Implementing an algorithm to find out the best match jobs."""
import csv
import sqlite3
import unicodedata

global total_count

text = []
labels = []
filename = 'SkillsetUniversal.txt'


def read_txt(file, text):
    """Reading data from text files."""
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            for item in row:
                text.append(item)
    return text


def db_time():
    """Reading data from tables."""
    conn = sqlite3.connect('stuffToPlot.db')
    c = conn.cursor()
    jobs = []
    for row in c.execute('SELECT DESCRIPTION FROM stuf'):
        jobs.append(row)
    # print len(jobs)
    c.close()
    c = conn.cursor()
    skills = []
    for row in c.execute('SELECT description FROM stuffToPlot'):
        skills.append(row)
    # print skills
    c.close()
    conn.close()
    return jobs, skills


def jobs_calc(job, text):
    """Calculate for each job how many skills required with set."""
    temp = 0
    for uni_word in text:
        if uni_word in job:
            temp += 1
    return temp

txt = read_txt(filename, labels)
jobs, skills = db_time()
for i in range(len(jobs)):
    jobs[i] = unicodedata.normalize('NFKD', "".join(jobs[i]).replace('\n', ' ').replace('\t', ' ')).encode('ascii','ignore')

# cz skills will just be in 1 cell
skills[0] = unicodedata.normalize('NFKD', "".join(skills[0])).encode('ascii', 'ignore')
skill_l = (skills[0].split(', '))
skill_list = [item.lower() for item in skill_l]
text = [item.lower() for item in txt]
jobss = [item.lower() for item in jobs]
wtf = []
for job in jobss:
    wtf.append(job.split(' '))

what = jobs_calc(skill_list, text)
what_jobs = []
worth = []
match = []
for job in wtf:
    x = jobs_calc(job, text)
    y = jobs_calc(job, skill_list)
    what_jobs.append(x)
    worth.append(y)
    match.append((float(y) / x) * 100)

# update it in sqlite and order this in desc.
print match

conn = sqlite3.connect('stuffToPlot.db')
sql = '''UPDATE stuf SET match = ? WHERE id = ?'''
for i in range(len(match)):
    cur = conn.cursor()
    cur.execute(sql, match[i], i + 1)
    conn.commit()
    cur.close()
conn.close()
