# import sqlite3

# # Connect to the database
# conn = sqlite3.connect("rrp.db")
# c = conn.cursor()

# # Enter the PID you want to delete
# pid_to_delete = 101  # Change this to the correct ID

# # Execute DELETE query
# c.execute("DELETE FROM professor WHERE pid = ?", (pid_to_delete,))

# # Commit the changes
# conn.commit()

# # Check if deletion was successful
# if c.rowcount > 0:
#     print(f"Professor with pid {pid_to_delete} deleted successfully!")
# else:
#     print("No record found with that pid.")

# # Close connection
# conn.close()


# Seein entries

import sqlite3

conn = sqlite3.connect("rrp.db")
c = conn.cursor()

# Fetch all records


#c.execute("INSERT INTO student (sid, sname,course, dept, year,sem,password) VALUES (?, ?, ?, ?, ?,?,?)",(1000, 'S1', 'CSM', 'CSE', 2,2,'12345'))
c.execute('SELECT * FROM student')
result = c.fetchone()
print(result)


# # Print results
# for row in rows:
#     print(row)
#conn.commit()
conn.close()
