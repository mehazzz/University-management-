# import sqlite3

# def display_tables(database):
#     try:
#         # Connect to the SQLite database
#         conn = sqlite3.connect(database)
#         cursor = conn.cursor()

#         # Query to get the list of tables
#         cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
#         tables = cursor.fetchall()
#         cursor.execute("Select * from Enrollments")
#         print(cursor.fetchall())

#         # Display the tables
#         if tables:
#             print("Tables in the database:")
#             for table in tables:
#                 print(table[0])
#         else:
#             print("No tables found in the database.")

#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")
#     finally:
#         if conn:
#             conn.close()

# # Replace 'your_database.db' with the path to your SQLite database file
# display_tables('university_management.db')




import sqlite3

def display_column_names(database, table_name):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(database)
        cursor = conn.cursor()

        # Query to get the column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        # Display the column names
        if columns:
            print(f"Column names in the table '{table_name}':")
            for column in columns:
                print(column[1])  # The second element in the tuple contains the column name
        else:
            print(f"No columns found in the table '{table_name}'.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# Replace 'your_database.db' with the path to your SQLite database file
# and 'Enrollments' with the name of the table you want to inspect
display_column_names('university_management.db', 'Enrollments')
