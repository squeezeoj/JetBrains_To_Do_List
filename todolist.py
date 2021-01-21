#----------------------------------------------------------------
# Imports
#----------------------------------------------------------------
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import table, column, select, update, insert
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from datetime import datetime, timedelta


#----------------------------------------------------------------
# Setup SQL Lite Database
#----------------------------------------------------------------
engine = create_engine('sqlite:///todo.db?check_same_thread=False')
Base = declarative_base()


#----------------------------------------------------------------
# Define Tasks Table
#----------------------------------------------------------------
class Tasks(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):
        return self.task


#----------------------------------------------------------------
# Create Tasks Table
#----------------------------------------------------------------
Base.metadata.create_all(engine)


#----------------------------------------------------------------
# Create Session
#----------------------------------------------------------------
Session = sessionmaker(bind=engine)
session = Session()

#----------------------------------------------------------------
# Print Database Utility
#----------------------------------------------------------------
def print_database():
    print("Tables",engine.table_names())
    inst = inspect(Table)
    attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
    print("Columns",attr_names)


#----------------------------------------------------------------
# To Do List Class
#----------------------------------------------------------------
class ToDoList:

    def __init__(self):
        pass

    #------------------------------------------------------------
    # Print Tasks for Date
    #   See: https://stackoverflow.com/questions/6446027/sqlalchemy-iterating-through-data
    #------------------------------------------------------------
    def get_tasks_for_date(self, prm_date, prm_print):
        print(prm_print)
        rows = session.query(Tasks).filter(Tasks.deadline == prm_date).all()
        row_count= len(rows)
        if row_count == 0:
            print("Nothing to do!")
        else:
            i = 1
            for row in rows:
                print(str(i) + ". " + row.task)
                i = i + 1
        print()
        return True


    #------------------------------------------------------------
    # Delete Task for Date
    #------------------------------------------------------------
    def delete_task_for_date(self, prm_id):

        # Attempt 3: Bypass SQLAlchemy ORM and use SQL directly...
        import sqlite3
        conn = sqlite3.connect("todo.db")
        cur = conn.cursor()
        cur.execute("DELETE FROM task WHERE id = {}".format(prm_id))
        conn.commit()

        # Attempt 2: Using hints section...
        ###rows = session.query(Tasks).order_by(Tasks.deadline).all()
        ###specific_row = rows[int(prm_id) - 1]
        ###session.delete(specific_row)
        ###session.commit()

        # Attempt 1: Based on what I read...
        ###rows = session.query(Tasks).filter(Tasks.id == prm_id).all()
        ###specific_row = rows[0] # First One
        ###session.delete(specific_row)
        ###session.commit()
        
        print("The task has been deleted!")
        return True


    #------------------------------------------------------------
    # Print Tasks
    #   See: https://stackoverflow.com/questions/6446027/sqlalchemy-iterating-through-data
    #------------------------------------------------------------
    def get_tasks(self, period="ALL", display=False):
        
        if period.upper() == "TODAY":
            today = datetime.today()
            arg_print = "Today " + today.strftime('%d %b') + ":"
            self.get_tasks_for_date(today.date(), arg_print)
            return True
        
        elif period.upper() == "WEEK":
            start_date = datetime.today()
            end_date = start_date + timedelta(6)
            delta = timedelta(days=1)
            while start_date <= end_date:
                arg_print = start_date.strftime('%A %d %b') + ":"
                self.get_tasks_for_date(start_date.date(), arg_print)
                start_date = start_date + delta
            return True

        elif period.upper() == "ALL":
            print("All Tasks:")
            rows = session.query(Tasks).order_by(Tasks.deadline).all()
            row_count= len(rows)
            if row_count == 0:
                print("Nothing to do!")
                task_dict = None
            else:
                # Create dictionary of tasks to be returned
                task_dict = dict()
                i = 1
                for row in rows:
                    if display:
                        print("{0}. {1}. {2} {3}".format(i, row.task, row.deadline.day, row.deadline.strftime('%b')))
                    d = dict()
                    d[i] = row.id
                    task_dict.update(d)
                    i = i + 1
            return task_dict

        elif period.upper() == "MISSED":
            rows = session.query(Tasks).filter(Tasks.deadline < datetime.today().date()).order_by(Tasks.deadline).all()
            row_count= len(rows)
            if row_count == 0:
                print("Nothing is missed!")
                task_dict = None
            else:
                # Create dictionary of tasks to be returned
                task_dict = dict()
                i = 1
                for row in rows:
                    if display:
                        print("{0}. {1}. {2} {3}".format(i, row.task, row.deadline.day, row.deadline.strftime('%b')))
                    d = dict()
                    d[i] = row.id
                    task_dict.update(d)
                    i = i + 1
            return task_dict
            

    #------------------------------------------------------------
    # Add New Task
    #   See: https://stackoverflow.com/questions/7889183/sqlalchemy-insert-or-update-example
    #------------------------------------------------------------
    def add_new_task(self, new_task, new_deadline):
        new_deadline = datetime.strptime(new_deadline, '%Y-%m-%d')
        adding_task = Tasks(task = new_task, deadline = new_deadline.date())
        session.add(adding_task)
        session.commit()
        return True

    #------------------------------------------------------------
    # Print Main Menu
    #------------------------------------------------------------
    def main_menu(self):
        while True:
            print()
            print("1) Today's tasks")
            print("2) Week's tasks")
            print("3) All tasks")
            print("4) Missed tasks")
            print("5) Add task")
            print("6) Delete task")
            print("0) Exit")
            main_choice = int(input())
            if main_choice == 1:            # Print Today's Tasks
                self.get_tasks(period="today", display=True)
            elif main_choice == 2:          # Print Week's Tasks
                self.get_tasks(period="week", display=True)
            elif main_choice == 3:          # Print All Tasks
                task_dict = self.get_tasks(period="all", display=True)
            elif main_choice == 4:          # Print Missed Tasks
                print("Missed Tasks:")
                self.get_tasks(period="missed", display=True)
            elif main_choice == 5:          # Add New Task
                print("\nEnter task")
                new_task = input()          # > Input String
                print("Enter deadline")
                new_deadline = input()      # > Input YYYY-MM-DD
                result = self.add_new_task(new_task, new_deadline)
                print("The task has been added!")
            elif main_choice == 6:          # Delete Task
                task_dict = self.get_tasks(period="all", display=False)
                if task_dict != None:
                    print("Choose the number of the task you want to delete:")
                    task_dict = self.get_tasks(period="all", display=True)
                    delete_task_id = int(input())
                    self.delete_task_for_date(task_dict[delete_task_id])
            else:                           # Exit
                print("\nBye!")
                break


#----------------------------------------------------------------
# Run the To Do List Program
#----------------------------------------------------------------
to_do_list = ToDoList()
to_do_list.main_menu()

