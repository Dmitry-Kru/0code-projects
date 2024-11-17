class Task:
    def add_task(self, name, description, due_date, status='Не выполнено'):
        self.description = description
        self.due_date = due_date
        self.status = status
        tasks_list.append(self.__dict__)
    def done(self):
        self.status = 'Выполнено'
    def incomplete_tasks():
        flag = 1
        for task in tasks_list:
            if task['status'] == 'Не выполнено':
                flag = 0
                print(f'Не выполнена задача:\n{task['description']}')
        if flag:
            print('Нет невыполненных задач')

tasks_list = []
task_1 = Task()
task_1.add_task('task_1', 'Задача 1', '25.11')
task_2 = Task()
task_2.add_task('task_2', 'Задача 2', '20.12')
task_3 = Task()
task_3.add_task('task_3', 'Задача 3', '25.12')
task_1.done()

print(tasks_list)
Task.incomplete_tasks()