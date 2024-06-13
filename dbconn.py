import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='34.128.72.144', #host
            user='root',
            password='1234567890',
            database='budget_db'
        )
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def save_budget_request(income, primary, secondary, tertiary):
    connection = create_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        query = """INSERT INTO budget_requests (income, primary_budget, secondary_budget, tertiary_budget)
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (income, primary, secondary, tertiary))
        connection.commit()
        return True
    except Error as e:
        print(f"Error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
