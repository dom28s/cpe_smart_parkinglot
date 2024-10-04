from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

# MySQL database connection settings
db_config = {
    'host': "100.124.147.43",
    'user': "admin",
    'password': "admin",
    'database': "projects"
}

# Function to connect to the database and get the FreeSpace data
def get_parking_data():
    try:
        # Open a new connection for each request
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Corrected query to select FreeSpace where ParkingLot_ID = 11
        cursor.execute("SELECT FreeSpace FROM `parkinglot` WHERE ParkingLot_ID = 11")

        # Fetch the result
        status = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Access the FreeSpace value and return it as an integer
        if status:
            freespace_value = status[0][0]  # Assuming only one row returned
            return int(freespace_value)  # Return the FreeSpace as an integer
        
        return None
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Flask route to send parking data as JSON
@app.route('/api/parking', methods=['GET'])
def api_parking():
    freespace_value = get_parking_data()
    if freespace_value is not None:
        return jsonify({"status": "success", "freespace": freespace_value})
    else:
        return jsonify({"status": "error", "message": "Unable to retrieve freespace data"})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=True)
