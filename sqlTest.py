import mysql.connector

mydb = mysql.connector.connect(
  host="100.124.147.43",  # Use the IP address without 'http://'
  user="root",  # Replace with your MySQL username
  database="projects",  # Replace with your database name
  port=3306  # MySQL default port, modify if different
)

# Create a cursor object
mycursor = mydb.cursor()
print('sdsd')

# # Execute a query
mycursor.execute("SELECT * FROM `admin`")

# # Fetch the results
result = mycursor.fetchall()

# # Print the results
for row in result:
     print(row[3])

# # Close the connection
mydb.close()

