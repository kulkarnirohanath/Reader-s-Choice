import os
from flask import Flask
import csv
import psycopg2

#Connect to the database
conn = psycopg2.connect("host=ec2-52-70-15-120.compute-1.amazonaws.com dbname=df44sa70pig1i1 user=znigfbuzkfpomr password=91d462e393b048ad4d5fef35bc1ac55e8c7486e6f9c93d99164d8af9d267b564")
cursor = conn.cursor()

#Open the CSV file
with open(r"C:\Users\Ruhan\CS51\project1\project1\books.csv","r") as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=",")

    #skip over the first row
    next(csv_reader)

    #iterate over each row and add it to the database
    for row in csv_reader:
        query = """INSERT INTO bookdetails (isbn, title, author, year) VALUES (%s, %s, %s, %s)"""
        data = (row[0], row[1], row[2], row[3])
        cursor.execute(query, data)
        conn.commit()
        
print("Job successfully done!!")
