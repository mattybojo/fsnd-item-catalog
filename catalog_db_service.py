from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Category, CategoryItem, User, Base


class CatalogDbService:

    def __init__(self):
        engine = create_engine('sqlite:///itemcatalog.db')
        Base.metadata.bind = engine
        db_session = sessionmaker(bind=engine)
        self.session = db_session()

    # Category

    def get_categories(self):
        return self.session.query(Category).all()

    def create_category(self, name, user_id):
        category = Category(name=name,
                            user_id=user_id)
        self.session.add(category)
        self.session.commit()
        return category.id

    def update_category(self, category):
        self.session.add(category)
        self.session.commit()

    def delete_category_by_id(self, id):
        category = self.session.query(Category).filter_by(id=id).one()
        self.session.delete(category)
        self.session.commit()

    # CategoryItem

    def get_item_by_id(self, id):
        return self.session.query(CategoryItem).filter_by(id=id).all()

    def get_items_by_category_id(self, id):
        return self.session.query(CategoryItem).filter_by(category_id=id).all()

    # TODO - how to get the latest items added to the DB
    def get_latest_items(self):
        return None

    def create_item(self, name, description, category_id, user_id):
        item = CategoryItem(name=name,
                            description=description,
                            category_id=category_id,
                            user_id=user_id)
        self.session.add(item)
        self.session.commit()
        return item.id

    def update_item(self, item):
        self.session.add(item)
        self.session.commit()

    def delete_item_by_id(self, id):
        item = self.session.query(CategoryItem).filter_by(id=id).one()
        self.session.delete(item)
        self.session.commit()

    # User
    def get_user_by_id(self, id):
        return self.session.query(User).filter_by(id=id).all()

    def get_user_id_by_email(self, email):
        user = self.session.query(User).filter_by(email=email).one()
        return user.id

    def create_user(self, name, email, picture):
        user = User(name=name,
                    email=email,
                    picture=picture)
        self.session.add(user)
        self.session.commit()
        return user.id

    def create_user_by_session(self, login_session):
        user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
        self.session.add(user)
        self.session.commit()
        return user.id

    def update_user(self, user):
        self.session.add(user)
        self.session.commit()

    def delete_user_by_id(self, id):
        user = self.session.query(User).filter_by(id=id).one()
        self.session.delete(user)
        self.session.commit()
