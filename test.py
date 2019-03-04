from index import UserModel, DB, TicketModel, NewsModel

db = DB()
user_model = UserModel(db.get_connection())
user_model.init_table()
print(user_model.get_all())