from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import sys


# Класс, от которого будет наследоваться созданный нами класс таблицы
Base = declarative_base()


# Наш класс таблицы для заданий
class Task(Base):

    # Название таблицы
    __tablename__ = 'task'

    # Колонки таблицы. primary_key - что-то типа автоиндексирования (то есть у каждой строчки будет автоматически
    # проставнлен номер)
    id = Column(Integer, primary_key=True)
    task = Column(String, default='default_value')
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):

        # Если мы будем вызывать объект Task, например на печатать, будет выдываться только задание
        return self.task


# Класс списка задач
class Todo:
    def __init__(self):
        """Мы сразу выполняем подключение к базе данных, как только класс создан"""

        # Подключение к базе данных
        self.engine = create_engine('sqlite:///todo.db')

        # Создаем сессию
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # Создаем базу данных (если она не создана)
        Base.metadata.create_all(self.engine)

        # Сегодняшняя дата, пригодится в будущем
        self.today_ = datetime.today().date()

    def main_menu(self):
        while True:
            print('''1) Show tasks
2) Add task
3) Delete task
0) Exit''')
            user_option = int(input('Enter number > '))
            if user_option == 1:
                self.show_menu()
            elif user_option == 2:
                self.add_task()
            elif user_option == 3:
                self.delete_task()
            elif user_option == 0:
                sys.exit()
            else:
                print('Enter the number!')
            print()

    def show_menu(self):
        """Вызывается, если пользователь выбрал 'Show tasks' """
        print('''1) Today's tasks
2) Week's tasks
3) All tasks
4) Missed tasks''')
        user_option = int(input('Enter number > '))
        if user_option == 1:
            self.show_tasks(time=1)
        elif user_option == 2:
            self.show_tasks(time=7)
        elif user_option == 3:
            self.show_tasks(time='all')
        elif user_option == 4:
            self.missed_tasks()

    def show_tasks(self, time='all'):
        """Отвечает за показ заданий. Функция может показывать задания за выбранное количество дней (time)"""

        # Делаем запрос в нашу таблицу - query(Task), сортируем по дате - order_by(Task.deadline). То есть получаем все
        # задания, отсортированные по дате
        tasks = self.session.query(Task).order_by(Task.deadline)
        nothing = 'Nothing to do!'

        # Если у time значение all, значит мы хотим посмотреть все задания
        if time == 'all':

            # print для красоты отображения
            print()

            # Если в списке нет значений, пишем, что ничего нет
            if not tasks:
                print(nothing)

            # В противном случае печаетаем все задания
            else:
                self.print_tasks(tasks)

        # Если же у time значение числовое, то есть мы хотим узнать задания за определенное количество дней,
        # то мы распечаетаем задания для каждого дня
        elif type(time) == int:

            # Составляем список дней, за которые мы хотим узнать задания.
            # timedelta дает указанное время (в нашем случае в днях), мы просто прибавляем к сегодняшней дате 0 дней,
            # 1 день и т.д. до значения time. Если значение time - 7, мы получим 7 дней
            dates = [self.today_ + timedelta(days=day) for day in range(0, time)]

            # Проходим по каждой дате
            for date in dates:
                print()

                # Печатаем дату в формате "Monday 28 Apr."
                print(date.strftime('%A'), date.day, date.strftime('%b'))

                # Ищем все задания за эту дату
                day_tasks = tasks.filter(Task.deadline == date).all()

                # Если задания есть, выводим их ниже даты
                if day_tasks:
                    print(*day_tasks, sep='\n')

                # В противном случае, пишем, что ничего нет
                else:
                    print(nothing)

    def missed_tasks(self):
        """Печатаем пропущенные задания (которые были до сегодняшней даты)"""
        print()

        # Отбираем задания, которые были до сегодняшней даты
        tasks = self.session.query(Task).filter(Task.deadline < self.today_).all()

        # Если они есть, печатаем их
        if tasks:
            print('Missed tasks:')
            self.print_tasks(tasks)
        else:
            print('Nothing is missed!')

    def add_task(self):
        """Добавляем задание"""
        try:

            # Просим ввести само задание
            user_task = input('Enter task:\n> ')

            # Дату задания
            user_deadline = input('Enter deadline:\n> ')

            # Переводим введенную дату в формат для записи
            user_deadline = datetime.strptime(user_deadline, '%Y-%m-%d')

            # Создаем объект класса нашей таблицы
            new_task = Task(task=user_task, deadline=user_deadline)

            # Добавляем в сессию новую стрчоку
            self.session.add(new_task)

            # Передаем изменения
            self.session.commit()
            print('The task has been added!')

        # Если что-то пошло не так, значит пользователь ввел некорректные данные
        except:
            print('Incorrect data')

    def delete_task(self):
        """Удаляем задание"""

        # Получаем список всех заданий
        tasks = self.session.query(Task).order_by(Task.deadline).all()
        print()

        # Проверяем, есть ли задания
        if tasks:
            print('Chose the number of the task you want to delete:')

            # Выводим список всех заданий
            self.print_tasks(tasks)

            # Добавляем функцию вернуться в главное меню
            print('0. Back to main menu')

            # Узнаем, какое задание пользователь хочет удалить
            task_to_delete = int(input('> '))

            # Если пользователь хочет вернуться в главное меню, ничего не возвращаем
            if task_to_delete == 0:
                return

            # Отнимаем единичку, потому что в питоне индекс начинается с 0, а не с 1
            task_to_delete -= 1

            # Получаем индекс задания, которое хотим удалить
            index = tasks[task_to_delete].id

            # Находим это задание и удаляем
            self.session.query(Task).filter(Task.id == index).delete()

            # Передаем изменения
            self.session.commit()
            print('The task has been deleted!')

        # Если заданий нет, так и пишем
        else:
            print('Nothing to delete')

    def print_tasks(self, tasks):
        """Печатаем задания. На вход получает список всех заданий"""
        for num, task in enumerate(tasks, 1):

            # Печатаем в формате (порядковый номер) (задание) (дата)
            print(f'{num}. {task}. {task.deadline.day} {task.deadline.strftime("%b")}')

    def print_table(self):
        """Функция просто печатает таблицу. Нужна для тестов кода"""
        for i in self.session.query(Task).order_by(Task.id):
            print(i.id, i.task, i.deadline)


if __name__ == '__main__':
    my_tasks = Todo()
    my_tasks.main_menu()


