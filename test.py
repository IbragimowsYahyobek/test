
import sqlite3

class DatabaseManager:
    def __init__(self, name):
        self.db_name = name
        self.connection = None

    def open_connection(self):
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.name)
                print("Соединение с базой данных успешно открыто.")
            except sqlite3.Error as e:
                print(f"Ошибка при открытии соединения: {e}")

import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = None

    def open_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_name)
            self.connection.row_factory = sqlite3.Row  

    def close_connection(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def execute_query(self, query, params=()):
        self.open_connection()
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor

    def fetch_one(self, query, params=()):
        cursor = self.execute_query(query, params)
        return cursor.fetchone()

    def __enter__(self):
        self.open_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close_connection()

class User:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.create_table()

    def create_table(self):
        execute = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
        """
        self.db_manager.execute_execut(execute)

    def add_user(self, name, email):
        execute = "INSERT INTO users (name, email) VALUES (?, ?)"
        self.db_manager.execute_execute(execute, (name, email))

    def get_user(self, user_id):
        query = "SELECT * FROM users WHERE id = ?"
        return self.db_manager.fetch_one(query, (user_id,))

    def delete_user(self, user_id):
        query = "DELETE FROM users WHERE id = ?"
        self.db_manager.execute_query(query, (user_id,))

if __name__ == "__main__":
    db_manager = DatabaseManager("example.db")
    
    with db_manager:
        user_manager = User(db_manager)
        
        user_manager.add_user("Yahyo", "Yahyo@example.com")
        
        user = user_manager.get_user(1)
        print(dict(user)) if user else print("Пользователь не найден.")
    
        user_manager.delete_user(1)




class Admin(User):
    def create_table(self):
        super().create_table()
        execute = """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,
            role TEXT NOT NULL,
            FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(execute)

    def add_admin(self, name, email, role):
        self.add_user(name, email)
        query = "INSERT INTO admins (id, role) VALUES (?, ?)"
        user_id = self.db_manager.fetch_one("SELECT id FROM users WHERE email = ?", (email,))['id']
        self.db_manager.execute_query(query, (user_id, role))

    def get_admin(self, user_id):
        query = """
        SELECT u.*, a.role 
        FROM users u
        JOIN admins a ON u.id = a.id
        WHERE u.id = ?
        """
        return self.db_manager.fetch_one(query, (user_id,))

class Customer(User):
    def create_table(self):
        super().create_table()
        execute = """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            address TEXT NOT NULL,
            FOREIGN KEY (id) REFERENCES users (id) ON DELETE CASCADE
        )
        """
        self.db_manager.execute_query(execute)

    def add_customer(self, name, email, address):
        self.add_user(name, email)  
        query = "INSERT INTO customers (id, address) VALUES (?, ?)"
        user_id = self.db_manager.fetch_one("SELECT id FROM users WHERE email = ?", (email,))['id']
        self.db_manager.execute_query(query, (user_id, address))

    def get_customer(self, user_id):
        query = """
        SELECT u.*, c.address 
        FROM users u
        JOIN customers c ON u.id = c.id
        WHERE u.id = ?
        """
        return self.db_manager.fetch_one(query, (user_id,))

if __name__ == "__main__":
    db_manager = DatabaseManager("example.db")
    
    with db_manager:
        admin_manager = Admin(db_manager)
        customer_manager = Customer(db_manager)
        
        admin_manager.add_admin("", "bob@example.com", "Super Admin")
    
        admin = admin_manager.get_admin(1) 
        print(dict(admin)) if admin else print("Администратор не найден.")
        
        customer_manager.add_customer("Yahyo", "yahyo@example.com", "123 Main St")
        
        customer = customer_manager.get_customer(1)
        print(dict(customer)) if customer else print("Клиент не найден.")
                     