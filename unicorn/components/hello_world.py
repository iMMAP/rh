from django_unicorn.components import UnicornView


class HelloWorldView(UnicornView):
    task = ""
    tasks = []

    def add(self):
        self.tasks.append(self.task)
        self.task = ""