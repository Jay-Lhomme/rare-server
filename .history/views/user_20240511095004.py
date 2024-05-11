import sqlite3
import json
from datetime import datetime
from models import User, Serialized, SerializedUserManagement


def login_user(user):
    """Checks for the user in the database

    Args:
        user (dict): Contains the username and password of the user trying to login

    Returns:
        json string: If the user was found will return valid boolean of True and the user's id as the token
                     If the user was not found will return valid boolean False
    """
    with sqlite3.connect('./db.sqlite3') as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("""
            select id, username
            from Users
            where username = ?
            and password = ?
        """, (user['username'], user['password']))

        user_from_db = db_cursor.fetchone()

        if user_from_db is not None:
            response = {
                'valid': True,
                'token': user_from_db['id']
            }
        else:
            response = {
                'valid': False
            }

        return json.dumps(response)

def create_user(user):
    """Adds a user to the database when they register

    Args:
        user (dictionary): The dictionary passed to the register post request

    Returns:
        json string: Contains the token of the newly created user
    """
    with sqlite3.connect('./db.sqlite3') as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()
        
        # Use the get method to provide a default value if the key does not exist
        profile_image_url = user.get('profile_image_url', 'default_image_url')

        db_cursor.execute("""
        INSERT INTO Users (first_name, last_name, username, email, password, profile_image_url, bio, created_on, active) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (
            user['first_name'],
            user['last_name'],
            user['username'],
            user['email'],
            user['password'],
            profile_image_url,  # Use the variable here
            user['bio'],
            datetime.now()
        ))

        id = db_cursor.lastrowid

        return json.dumps({
            'token': id,
            'valid': True
        })
def update_user(id, new_user):
    with sqlite3.connect("./db.sqlite3") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
        UPDATE Users
            SET
                first_name = ?,
                last_name = ?,
                username = ?,
                email = ?,
                password = ?,
                profile_image_url = ?,
                bio = ?
        WHERE id = ?
        """, (new_user['first_name'], new_user['last_name'],
              new_user['username'], new_user['email'],
              new_user['password'], new_user['profile_image_url'],
              new_user['bio'], id, ))

        # Commit the transaction
        conn.commit()

        # Were any rows affected?
        # Did the client send an `id` that exists?
        rows_affected = db_cursor.rowcount

    # return value of this function
    if rows_affected == 0:
        # Forces 404 response by main module
        return False
    else:
        # Forces 204 response by main module
        return True
    
def get_all_users():
    # Open a connection to the database
    with sqlite3.connect("./db.sqlite3") as conn:

        # Just use these. It's a Black Box.
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        SELECT
            u.id,
            u.first_name,
            u.last_name,
            u.email,
            u.bio,
            u.username,
            u.profile_image_url,
            u.created_on,
            u.active
        FROM Users u
        """)

        # Initialize an empty list to hold all animal representations
        users = []

        # Convert rows of data into a Python list
        dataset = db_cursor.fetchall()

        # Iterate list of data returned from database
    for row in dataset:
        serialized_user = Serialized(row['id'], row['first_name'], row['last_name'], row['email'], row['bio'], row['username'], row['profile_image_url'], row['created_on'], row['active'])
        users.append(serialized_user.__dict__)

    return users

def get_single_user(id):
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("""
        SELECT
            u.id,
            u.first_name,
            u.last_name,
            u.email,
            u.bio,
            u.username,
            u.password,
            u.profile_image_url,
            u.created_on,
            u.active
        FROM Users u
        WHERE u.id = ?
        """, ( id, ))

        data = db_cursor.fetchone()

        # Check if data is not None before trying to access its items
        if data is not None:
            user = User(data['id'], data['first_name'], data['last_name'],
                        data['email'], data['bio'], data['username'], data['password'],
                        data['profile_image_url'], data['created_on'], data['active'])
        
            return user.__dict__
        else:
            return None

def get_all_users_management():
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute("""
        SELECT
            u.id,
            u.first_name,
            u.last_name,
            u.email,
            u.username
        FROM Users u
        ORDER BY u.username COLLATE NOCASE ASC
        """)

        dataset = db_cursor.fetchall()
        users_management = []

        for row in dataset:
            user_management = SerializedUserManagement(row['username'], row['first_name'], row['last_name'], row['email'])
            users_management.append(user_management.__dict__)

    return users_management

def delete_user(id):
    """Deletes a user from the database.

    Args:
        id (int): The ID of the user to delete.
    """
    with sqlite3.connect('./db.sqlite3') as conn:
        db_cursor = conn.cursor()

        db_cursor.execute("""
            DELETE FROM Users
            WHERE id = ?
        """, (id,))
