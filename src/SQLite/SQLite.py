
import os
import sqlite3


class SQLITE:
    def __init__(self, dbName = './APKcrawler.db'):
        self.con = sqlite3.connect(dbName)
        self.cur = self.con.cursor()
        self.base = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(self.base, 'sql/create.sql')) as f:
            self.cur.execute(f.read())

    def build_set(sefl, set):
        return ', '.join([ f"{key} = '{value}'" if value else f"{key} = NULL" for key, value in set.items() ])

    def build_where(self, where):
        if where:
            wheres = []
            for key, value in where.items():
                if value:
                    if value == "NOT NULL": wheres += [ f"{key} IS NOT NULL" ]
                    else: wheres += [ f"{key} IS '{value}'" ]
                else: wheres += [ f"{key} IS NULL" ]
            return f" WHERE {' AND '.join(wheres)}"
        return ""

    def create(self, package_name = None, installs = 0):
        create = f"INSERT INTO AppList (package_name, installs) VALUES ('{package_name}', {installs})"

        if len(self.read({'package_name': package_name})) == 0:
            self.cur.execute(create)
            self.con.commit()
            return True
        return False

    def read(self, where = None):
        with open(os.path.join(self.base, 'sql/select.sql')) as f:
            read = f.read() + self.build_where(where)

        return [ package[0] for package in self.cur.execute(read) ]

    def update(self, set = None, where = None):
        update = f"UPDATE AppList SET {self.build_set(set)}" + self.build_where(where)

        self.cur.execute(update)
        self.con.commit()


if __name__ == '__main__':
    sqlite = SQLITE()

    # C
    if sqlite.create("com.supercell.brawlstars"):
        print("Success to create")

    # R
    print(sqlite.read({"install_date": None, "extract_date": None}))

    import datetime

    # U
    sqlite.update(
        set = {
            "install_date": datetime.datetime.now(),
            "installs": 500000
        }, 
        where = {
            "install_date": None,
            "extract_date": None
        }
    )
