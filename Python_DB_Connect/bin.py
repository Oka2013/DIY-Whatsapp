from contextlib import nullcontext

from db import DataBaseAgent

class Bin:
    def __init__(self, MAX_BIN_COUNT, db_name, dba):
        self.db_name = db_name
        self.MAX_BIN_COUNT = MAX_BIN_COUNT
        self.bin_content = []
        self.dba = dba

    def add(self, data):
        if not data in self.bin_content:
            self.bin_content.append(data)

    def empty(self):
        print(f"**************************\nThe BIN for {self.db_name} will be EMPTIED\nData that will be deleted :")

        for element in self.bin_content:
            print(f"Element {element} of {self.db_name}")

        if input("Are you sure (n for No, y for Yes) ? ") == "n":
            return

        self.dba.execute_on_db(f"delete from {self.db_name} where id in ({",".join(map(str, self.bin_content))})")

        self.bin_content = []

    def update(self):
        if len(self.bin_content) > self.MAX_BIN_COUNT:
            self.empty()