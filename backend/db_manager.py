import pyodbc

class DBManager():
    """
        This class is to manage all the functions to use the SQL database service.
        It handles the connection to the database, the execution of queries, and the retrieval of data.
        It also provides methods to insert data into the database.
        It uses the pyodbc library to connect to the database.
        It uses the parameters dictionary to get the connection string.
        It uses the users table to get the users information.
        It uses the conversation history table to store the conversation history.

    """
    def __init__(self,
                 parameters: dict[str, any]):
        self.parameters = parameters
        self.users_rows = self.__get_users_rows()

    def __get_users_rows(self):
        """
        Gets the users information from the database.
        Returns:
            list: A list of tuples, where each tuple represents a row in the users table.
        """
        # Connect to the database
        conn = pyodbc.connect(self.parameters['sql_conn_str'])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows

    def get_users_info(self):
        """
        Gets the users information from the database.
        Returns:
            dict: A dictionary where the keys are usernames and the values are dictionaries containing user details.
        """
        users_info = {}
        for row in self.users_rows:
            user = {'email': row[2],
                    'failed_login_attempts': row[3],
                    'logged_in': row[4],
                    'name': row[5],
                    'password': row[6],
                    'roles': eval(row[7])}
            users_info.update({row[1]: user})
        return users_info
    
    def get_user_rows(self):
        return self.users_rows
    
    def get_user_id(self, username):
        for user in self.users_rows:
            if user[1] == username:
                return user[0]
            
    def validate_user_max_messages(self, user_id):
        """
        Validates if the user has reached the maximum number of messages allowed.
        Args:
            user_id (int): The ID of the user.
        Returns:
            bool: True if the user has not reached the maximum number of messages, False otherwise.
        """
        cant_user_messages = self.get_cant_user_messages(user_id)
        user_max_messages = self.get_user_max_messages(user_id)
        if cant_user_messages < user_max_messages:
            return True
        else:
            return False

    def get_user_max_messages(self, user_id):
        for user in self.users_rows:
            if user[0] == user_id:
                return user[8]
    
    def get_cant_user_messages(self, user_id):
        """
        Gets the number of messages sent by the user.
        Args:
            user_id (int): The ID of the user.
        Returns:
            int: The number of messages sent by the user.
        """
        sql_query = f"""SELECT count(*) FROM ConversationHistory
                        WHERE UserID = {user_id}"""
        conn = pyodbc.connect(self.parameters['sql_conn_str'])
        cursor = conn.cursor()
        cursor.execute(sql_query)
        cant_user_messages = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return cant_user_messages

    def insert_conversation(self, user_id, user_query, chatbot_aswer):
        """
        Inserts a new conversation record into the ConversationHistory table.
        Args:
            user_id (int): The ID of the user.
            user_query (str): The user's query.
            chatbot_aswer (str): The chatbot's response.
        """
        conn = pyodbc.connect(self.parameters['sql_conn_str'])
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ConversationHistory(UserID, UserQuery, ChatBotAnswer) VALUES (?, ?, ?)",
                             user_id, user_query, chatbot_aswer)
        conn.commit()
        cursor.close()  
        conn.close() 
    
    def create_users_table(self):
        conn = pyodbc.connect(self.parameters['sql_conn_str'])
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE [dbo].[Users] (
            [ID]                 INT           IDENTITY (1, 1) NOT NULL,
            [UserName]           VARCHAR (255) NOT NULL,
            [Email]              VARCHAR (255) NULL,
            [FailedLoginAttemps] INT           CONSTRAINT [DEFAULT_Users_FailedLoginAttemps] DEFAULT ((0)) NOT NULL,
            [LoggedIn]           BIT           CONSTRAINT [DEFAULT_Users_LoggedIn] DEFAULT ((0)) NOT NULL,
            [Name]               VARCHAR (255) NOT NULL,
            [Password]           VARCHAR (255) NOT NULL,
            [Roles]              VARCHAR (255) NOT NULL,
            [max_messages]       INT           CONSTRAINT [DEFAULT_Users_max_messages] DEFAULT ((15)) NULL,
            PRIMARY KEY CLUSTERED ([ID] ASC),
            UNIQUE NONCLUSTERED ([UserName] ASC)
        );
        """)
        conn.commit()

    def create_conversationHistory_table(self):
        sql_query = """
            CREATE TABLE [dbo].[ConversationHistory] (
            [ID]                 INT           IDENTITY (1, 1) NOT NULL,
            [UserID]             INT NOT NULL,
            [DateTime]           DATETIME NOT NULL default(current_timestamp),
            [UserQuery]          NVARCHAR (MAX) NOT NULL,
            [ChatBotAnswer]      NVARCHAR (MAX) NOT NULL,
            PRIMARY KEY CLUSTERED ([ID] ASC)
        );
        """
        conn = pyodbc.connect(self.parameters['sql_conn_str'])
        cursor = conn.cursor()
        cursor.execute(sql_query)
        conn.commit()
        
