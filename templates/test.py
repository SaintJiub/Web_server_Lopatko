from index import UserModel, DB, TicketModel, NewsModel

db = DB()
user_model = UserModel(db.get_connection())
news_model = NewsModel(db.get_connection())
user_model.init_table()
user_model.insert("lopatko","1")