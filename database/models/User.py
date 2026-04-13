from database import Interface

class User:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name

    def __eq__(self, other):
        return self.id == other.id




def userFromId(db: Interface.Interface, id: str):
    r = db.executeQuery("SELECT srcId, name FROM Users WHERE srcId = ?", (id,))
    if len(r) == 0:
        return None
    
    return User(r[0]['srcId'], r[0]['name'])