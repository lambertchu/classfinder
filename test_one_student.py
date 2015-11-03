import sys
import math
import csv
import psycopg2
from scipy import spatial

try:
    with open('pass.txt', 'r') as f:
        password = f.readline()
    conn = psycopg2.connect("dbname='lambertchu' user='postgres' host='lambertchu.lids.mit.edu' password='%s'" % password)
    print "Connected to database"
except:
    print "Unable to connect to the database"
    sys.exit()

# conn.cursor will return a cursor object that you can use to perform queries
cursor = conn.cursor()

# get list of all classes
cursor.execute("SELECT DISTINCT Subject FROM enrollment_data_updated")
classes = [cl[0] for cl in cursor.fetchall()]
num_classes = len(classes)
print num_classes

# create hash table with keys = classes and values = index in list
class_table = {k:v for k, v in zip(classes, xrange(num_classes))}


# create table with number of students that took each pair of classes
with open('output_matrix_updated.csv', 'r') as f:
    reader = csv.reader(f)
    shared_classes_table = list(reader)

# create hash table for total number of students that took each class
totals = {}
count = 0
for row in shared_classes_table:
    row_num = [int(x) for x in row]
    totals[classes[count]] = sum(row_num)
    count += 1

print len(shared_classes_table)
subjects = ['8.01', '18.02', '3.091', '7.016', '8.02', '6.042', '6.01', '6.004', '6.006', '6.034', '18.06', '6.005', '21M.030', '9.00', '6.813', '15.401']

GIR = ['18.01','18.01A','18.014','18.02A','18.02','18.022','18.024','8.01','8.01L','8.011','8.012','8.02','8.022','7.012','7.013','7.014','7.016','5.111','5.112','3.091']

# calculate "importance" of each class - we exclude current subjects from similarity comparisons
gir_importance = {}
in_major_importance = {}
hass_importance = {}
misc_importance = {}

for cl in classes:
    total = 1.0
    for subject in subjects:
        #if subject != cl:
        shared_number = int(shared_classes_table[class_table[cl]][class_table[subject]])
        total_number_subject = totals[subject]
        total *= math.exp(0.5 * shared_number / total_number_subject)
    
    # record total
    if cl in GIR:
        gir_importance[cl] = total
    elif cl.startswith("6."):
        in_major_importance[cl] = total
    else:
        misc_importance[cl] = total
    # may also include category for HASS


with open("lambert_importance_list.csv", "wb") as f:
    writer = csv.writer(f)
    
    writer.writerow(gir_importance.keys())
    gir_vals = [gir_importance[key] for key in gir_importance.keys()]
    writer.writerow(gir_vals)

    writer.writerow(in_major_importance.keys())
    major_vals = [in_major_importance[key] for key in in_major_importance.keys()]
    writer.writerow(major_vals)

    writer.writerow(misc_importance.keys())
    misc_vals = [misc_importance[key] for key in misc_importance.keys()]
    writer.writerow(misc_vals)

sys.exit()