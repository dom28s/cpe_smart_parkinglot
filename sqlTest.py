import mysql.connector

# Establish a connection to the database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="projects"
)

# Create a cursor object
mycursor = mydb.cursor()

# Execute a query
mycursor.execute("SELECT * FROM car")

# Fetch the results
result = mycursor.fetchall()

# Print the results
for row in result:
    print(row[3])

# Close the connection
mydb.close()
