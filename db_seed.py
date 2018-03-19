from catalog_db_service import CatalogDbService

service = CatalogDbService()

# Create dummy user
user1_id = service.create_user(name="Robo Barista",
                               email="tinnyTim@udacity.com",
                               picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')  # noqa

# Items for Horror Movies
category1_id = service.create_category(name="Horror Movies", user_id=user1_id)

service.create_item(name="It",
                    description="""In the summer of 1989, a group of bullied
                    kids band together to destroy a shapeshifting monster,
                    which disguises itself as a clown and preys on the children
                    of Derry, their small Maine town.""",
                    category_id=category1_id, user_id=user1_id)

service.create_item(name="Get Out",
                    description="""A young African-American visits his white
                    girlfriend's parents for the weekend, where his simmering
                    uneasiness about their reception of him eventually reaches
                    a boiling point.""",
                    category_id=category1_id, user_id=user1_id)

service.create_item(name="Halloween",
                    description="""Fifteen years after murdering his sister on
                    Halloween night 1963, Michael Myers escapes from a mental
                    hospital and returns to the small town of Haddonfield to
                    kill again.""",
                    category_id=category1_id, user_id=user1_id)

# Items for Comedies
category2_id = service.create_category(name="Comedy Movies", user_id=user1_id)

service.create_item(name="Super Troopers",
                    description="""Five Vermont state troopers, avid pranksters
                    with a knack for screwing up, try to save their jobs and
                    out-do the local police department by solving a crime.""",
                    category_id=category2_id, user_id=user1_id)

service.create_item(name="Out Cold",
                    description="""A snowboarder's plans for his own snowboard
                    park go awry when an ex-girlfriend returns to town.""",
                    category_id=category2_id, user_id=user1_id)

service.create_item(name="The Hangover",
                    description="""Three buddies wake up from a bachelor party
                    in Las Vegas, with no memory of the previous night and the
                    bachelor missing. They make their way around the city in
                    order to find their friend before his wedding.""",
                    category_id=category2_id, user_id=user1_id)

# Items for Dramas
category3_id = service.create_category(name="Drama Movies", user_id=user1_id)

service.create_item(name="Shawshank Redemption",
                    description="""Two imprisoned men bond over a number of
                    years, finding solace and eventual redemption through acts
                    of common decency.""",
                    category_id=category3_id, user_id=user1_id)

service.create_item(name="Titanic",
                    description="""A seventeen-year-old aristocrat falls in
                    love with a kind but poor artist aboard the luxurious,
                    ill-fated R.M.S. Titanic.""",
                    category_id=category3_id, user_id=user1_id)

service.create_item(name="Forrest Gump",
                    description="""The presidencies of Kennedy and Johnson,
                    Vietnam, Watergate, and other history unfold through the
                    perspective of an Alabama man with an IQ of 75.""",
                    category_id=category3_id, user_id=user1_id)

# Items for Documentaries
category4_id = service.create_category(name="Documentary Movies",
                                       user_id=user1_id)

categories = service.get_categories()
for category in categories:
    print "Category: " + category.name
