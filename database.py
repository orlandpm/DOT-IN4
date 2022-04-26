from builtins import dict, len, zip
import sqlite3
   
  
# conn = sqlite3.connect('SqliteDBnex.db')
# cur = conn.cursor()
  

class SqliteDBnexDatabase :
   

  def  __init__(self):

    self.execute_hash_query('CREATE TABLE IF NOT EXISTS "Birds" ( "Name"	TEXT NOT NULL, "User"	TEXT NOT NULL, "Bio"	TEXT NOT NULL, "Age"	INTEGER NOT NULL, "PasswordHash"	INTEGER NOT NULL, "BirdId"	INTEGER NOT NULL, PRIMARY KEY("BirdId" AUTOINCREMENT));')  
    self.execute_hash_query( 'CREATE TABLE IF NOT EXISTS  "Comment" ( "User" TEXT NOT NULL, "PostId"	INTEGER NOT NULL, "Comments"	TEXT NOT NULL,     PRIMARY KEY("PostId" AUTOINCREMENT));') 
    self.execute_hash_query('CREATE TABLE IF NOT EXISTS "Counts" ( "PostId"	INTEGER NOT NULL, "Likescount"	TEXT NOT NULL, "User"	TEXT NOT NULL,      PRIMARY KEY("PostId" AUTOINCREMENT));') 
    self.execute_hash_query('CREATE TABLE IF NOT EXISTS "Likes" ( "User"	TEXT NOT NULL, "PostId"	INTEGER NOT NULL, PRIMARY KEY("PostId" AUTOINCREMENT));')
    self.execute_hash_query('CREATE TABLE IF NOT EXISTS "Posts" ("PostId"	INTEGER NOT NULL, "Texts"	TEXT NOT NULL UNIQUE, "BirdId" INTEGER NOT NULL, PRIMARY KEY("PostId" AUTOINCREMENT));')



  def create_user(self,Name,User, Bio,Age, PasswordHash):
        self.execute_hash_query("""INSERT INTO Birds (Name,User,Bio,Age,PasswordHash) VALUES (?, ?, ?, ?, ?)""",Name,User, Bio,Age, PasswordHash)
 # conn.commit() 

        
  def get_user_by_Id(self,BirdId):
      return self.execute_query("SELECT * FROM Birds WHERE BirdId = ?",BirdId) 

  def get_id_by_user(self, user):
      return self.execute_query("SELECT * FROM Birds WHERE User = ?", user) 
 

     # if len(results) > 0:      
     # return results[0]
     # else:
     # return None

  def execute_hash_query(self, query_text, *parameters):
      conn = sqlite3.connect('SqliteDBnex.db')
      cur = conn.cursor()
      cur.execute(query_text, parameters)
      conn.commit()


  def execute_query(self, query_text, *parameters):
      conn = sqlite3.connect('SqliteDBnex.db')
      cur = conn.cursor()
      cur.execute(query_text, parameters)

      column_names = []
      for column in cur.description:
       column_names.append(column[0])

      rows = cur.fetchall()
      dicts = []
      for row in rows:
        d = dict(zip(column_names, row))
        dicts.append(d)
        conn.close()
      return dicts

  def get_posts_by_Id(self,user ):
        # return self.execute_query("""SELECT * FROM Posts WHERE PostId=?""",user)
        return self.execute_query("SELECT * FROM Posts Inner JOIN Birds ON Posts.BirdId = Birds.BirdId WHERE Birds.BirdId = ?;", user)

        
     

  def get_all_posts_by_Id(self, user):
        return self.execute_query("""SELECT Posts.User, Posts.Texts,Birds.Name, Counts.Likescount,DL.CurrentBirdLike FROM  Posts
                                    INNER JOIN Birds
                                    ON Posts.User = Birds.User
                                    INNER JOIN Counts 
                                    ON Counts.PostId = Posts.PostId
                                    LEFT JOIN Likes
                                    ON Posts.PostId = Likes.PostId
                                    INNER JOIN (SELECT Posts.PostId AS Id, COUNT(L.User) AS CurrentBirdLike FROM Posts
                                    LEFT JOIN (SELECT * FROM Likes WHERE User=?) AS L
                                    ON Posts.PostId = L.PostId
                                    GROUP BY Posts.PostId) AS DL
                                    ON Posts.PostId = DL.Id""", user)

  def  get_comment_by_Id(self,post_id):
       conn = sqlite3.connect('SqliteDBnex.db')
       cur = conn.cursor()
       self.execute_query("""SELECT * FROM Comment WHERE PostId = ?""",post_id)
       columns = [column[0] for column in cur.description]
       results = []
       for row in cur:
            d = dict(zip(columns,row))
            results.append(d)
       return results

  def insert_post(self, id, post_content):
    self.execute_hash_query("INSERT INTO Posts (Texts, BirdId) VALUES (?, ?)", post_content, id)
    pass

  def like_post(self, user, post_id):
      self.execute_hash_query("""INSERT INTO likes (User,PostId) VALUES (?,?)""",user,post_id)
        

 
  def like_count(self, post_id):
      data = self.execute_query("""SELECT COUNT(*) FROM Counts WHERE  PostId=? AND User=?""",post_id)
      return len(data)

  def already_liked(self,user, post_id):
      conn = sqlite3.connect('SqliteDBnex.db')
      cur = conn.cursor()
      self.execute_query("""SELECT COUNT(*) FROM likes WHERE  PostId = ? AND User = ?""",user,post_id)
      for row in cur:
         return (row[0] > 0)      

  def unlike_post(self, user, post_id):
      self.execute_hash_query("""DELETE FROM likes WHERE User=? And PostId=?""",user,post_id)

  def toggle_like(self,user,post_id):
      if self.already_liked(user,post_id):
           action = 'unlike'
           self.unlike_post(user,post_id)
      else:
            action = 'like'
            self.like_post(user,post_id)
      return {
             'like_count' : self.like_count(post_id),
             'action' : action
       } 

  def delete_post(self, post_id, user):
      self.execute_hash_query("""DELETE FROM Posts WHERE Id=? And User=?""", post_id, user)