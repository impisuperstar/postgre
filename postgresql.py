import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS phones(
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
            phone_number VARCHAR(20) NOT NULL
        );
        """)
        conn.commit()

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        try:
            cur.execute("""
            INSERT INTO clients (first_name, last_name, email)
            VALUES (%s, %s, %s)
            RETURNING id
            """, (first_name, last_name, email))
            client_id = cur.fetchone()[0]
            conn.commit()
            return client_id
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print(f"Ошибка: {e}")
            return None

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        try:
            cur.execute("""
            INSERT INTO phones (client_id, phone_number)
            VALUES (%s, %s)
            RETURNING id
            """, (client_id, phone))
            phone_id = cur.fetchone()[0]
            conn.commit()
            return phone_id
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print(f"Ошибка: {e}")
            return None

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    try:
        with conn.cursor() as cur:
            update_fields = []
            update_values = []
            
            if first_name is not None:
                update_fields.append("first_name = %s")
                update_values.append(first_name)
            
            if last_name is not None:
                update_fields.append("last_name = %s")
                update_values.append(last_name)
            
            if email is not None:
                update_fields.append("email = %s")
                update_values.append(email)
            
            if update_fields:
                update_query = f"""
                    UPDATE clients 
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                    RETURNING id
                """
                update_values.append(client_id)
                
                cur.execute(update_query, update_values)
                conn.commit()
                if cur.rowcount == 0:
                    return {"success": False, "message": "Клиент не найден"}
    except psycopg2.IntegrityError as e:
        conn.rollback()
        print(f"Ошибка: {e}")
        return None

def delete_phone(conn, client_id, phone):
    pass

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        try:
            cur.execute("""
            DELETE FROM clients
            WHERE id=%s
            """, (client_id,))
            conn.commit()
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print(f"Ошибка: {e}")
            return None

def find_client(conn, client_id):
    with conn.cursor() as cur:
        try:
            cur.execute("""
            SELECT id, first_name FROM clients
            WHERE id=%s
            """, (client_id,))
            print(cur.fetchone())
        except psycopg2.IntegrityError as e:
            conn.rollback()
            print(f"Ошибка: {e}")
            return None


with psycopg2.connect(database="users", user="msizov", password="") as conn:
    create_db(conn)

    client_id = add_client(conn, "Иван1", "Иванов", "ivanov1@example.com")
    if client_id:
        print(f"Клиент добавлен с ID: {client_id}")

    phone_id = add_phone(conn, 1, 89266028841)
    if phone_id:
        print(f"Клиент добавлен с ID: {phone_id}")

    change_client(conn, 2, 89266028843)

    #delete_client(conn, 2)

    find_client(conn, 22)

conn.close()