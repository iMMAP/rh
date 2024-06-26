## Best practices and coding guidelines

The following guidelines follow the PEP 8 style guide (https://www.python.org/dev/peps/pep-0008/) for general Python formatting rules.

### Styling 

- ***Naming Conventions***:

    - Use descriptive and meaningful names for variables, functions, classes, and modules.
    - Variable and function names should be in lowercase with words separated by underscores (snake_case).
    - Class names should follow the PascalCase convention (HelloWorld).
    - Module names should be in lowercase with words separated by underscores.
    - Use single leading underscores for non-public methods or attributes.
    - Use double leading underscores for name mangling.
Example of name mangling: 
```Python 

class MyClass:
    def __init__(self):
        self.__private_variable = 42

        #The MyClass has a private variable named __private_variable 
        # and a private method named __private_method(). 
        # The double leading underscores in their names indicate that they are 
        # intended to be used within the class and not accessed directly 
        # from outside the class.

    def __private_method(self):
        return "This is a private method."

    def public_method(self):
        return self.__private_method()

obj = MyClass()
print(obj.public_method())  # Output: This is a private method.


```
  
- ***Naming routes and urls***:
```python
app_name = 'projects'
{% url 'projects:project-list' %}

'projects/' -> name = 'projects-list'
'projects/create/' -> name = 'projects-create'
'projects/<int:pk>/' -> name = 'projects-detail'
'projects/<int:pk>/update/' ->  name = 'projects-update'
'projects/<int:pk>/delete/' -> name = 'projects-delete';
```
- ***REST Route conventions***:
    | Verb      | URI                  | Action  | Route Name     |   
    | --------- | -------------------- | ------- | -------------- |
    | GET       | /projects              | index   | projects.index   |  
    | GET       | /projects/create       | create  | projects.create  |     
    | POST      | /projects              | store   | projects.store   |   
    | GET       | /projects/{photo}      | show    | projects.show    |  
    | GET       | /projects/{photo}/edit | edit    | projects.edit    |   
    | PUT/PATCH | /projects/{photo}      | update  | projects.update  |    
    | DELETE    | /projects/{photo}      | destroy | projects.destroy | 


- ***Indentation and Formatting***:

    - Follow the ruff linting and formating rule run `make lint` to check for errors
    - Write clear, readable, and concise code. Avoid excessive nesting and complex logic. 

- ***Documentation***:

    - Provide clear and concise comments to explain the purpose and functionality of your code.
    - Use docstrings to document classes, functions, and modules.
    - Include parameter descriptions, return values, and examples whenever possible. 

- ***Error Handling***:
    
    - Handle exceptions gracefully. Use try-except blocks to catch and handle specific exceptions.
    - Avoid using bare except statements. 
    - Catch specific exceptions whenever possible.
    - Log error messages and stack traces to aid in debugging.
    - Raise custom exceptions when appropriate to provide informative error messages.

- ***Parameter typing***: 
   - Use Type Hints:
        - Utilise Python's type hinting feature introduced in Python 3.5 and above to annotate the types of function parameters.
   - Annotate the return type of a function using the -> syntax followed by the type.
    - Specify Parameter Types:
        - Annotate the types of function parameters using the : syntax followed by the type.
        - For example, def my_function(param1: int, param2: str) -> bool:
        - Use built-in types (e.g., int, str, list, dict) or import types from the typing module for more specific types (e.g., List, Dict, Tuple).
        - Use Union Types:
          - When a parameter can accept multiple types, use union types to specify all possible types.
          - Use the Union type from the typing module to annotate such parameters.
For example: 

```python
def process_data(data: Union[str, List[int]]) -> None:
```

### Code complexity:

- ***Cyclomatic complexity*** is a measure of the complexity and potential difficulty of understanding and maintaining a piece of code.
    - Aim to keep the cyclomatic complexity of individual functions and methods low.
    - Reduce complexity by breaking down complex functions into smaller, more manageable functions with clear responsibilities.
    - Use control flow statements (such as if, for, while) judiciously and avoid nested or deeply nested conditions.
    - Consider refactoring complex code blocks into separate functions or classes to improve readability and maintainability.

Example of cyclomatic complexity:

```python 
def print_matrix(matrix):
    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] % 2 == 0:
                print("Even")
            else:
                if matrix[i][j] > 0:
                    print("Positive")
                else:
                    print("Negative")
```

The code above has a very high cyclomatic complexity and contributes to poor performance.

### Logging 

- Identify what information should be logged, such as errors, warnings, debugging details, or important events.
    - Establish the level of verbosity and decide when to log at each level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
    - Be cautious when logging sensitive data, such as passwords or user information.

Example - how to create a logger in Python: 

```python 

import logging

# Create a logger object
logger = logging.getLogger(__name__)

# Set the logging level (optional)
logger.setLevel(logging.DEBUG)
# Log messages
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
logger.critical('Critical message')

```
### Security:
  
- Implement secure coding practices to prevent common vulnerabilities (e.g., SQL injection, cross-site scripting).
    - Sanitise user input to prevent malicious code execution.
    - Paramterise SQL queries.
    - Use secure password hashing algorithms like bcrypt or Argon2 for user authentication.
    - Ensure the protection of sensitive data by encrypting it when necessary.

- Be aware of the Top 10 OWASP (2017 - the list if frequently updated) while coding for web applications: 
    - Injection: This vulnerability refers to the ability for attackers to inject malicious code or commands into an application. Common examples include SQL injection, OS command injection, and LDAP injection.
    - Broken Authentication: This vulnerability occurs when there are flaws in the authentication and session management processes, leading to unauthorized access, session hijacking, or account takeover.
    - Sensitive Data Exposure: This vulnerability relates to the insecure handling or storage of sensitive data, such as passwords, credit card information, or personal data. It can occur due to weak encryption, inadequate access controls, or improper data handling.
    - XML External Entities (XXE): This vulnerability arises when an application processes XML input insecurely, allowing attackers to read local files, perform remote code execution, or launch denial-of-service attacks.
    - Broken Access Control: This vulnerability occurs when an application does not properly enforce access controls, allowing unauthorized users to access privileged functionality or perform actions they shouldn't be able to.
    - Security Misconfigurations: This vulnerability arises from insecure configurations, such as default settings, unused components, unnecessary features, or misconfigured security controls, that can be exploited by attackers.
    - Cross-Site Scripting (XSS): This vulnerability occurs when an application does not properly validate or sanitize user-supplied input, resulting in the execution of malicious scripts in users' browsers.
    - Insecure Deserialization: This vulnerability arises when an application deserializes untrusted data without proper validation, which can lead to remote code execution or denial-of-service attacks.
    - Using Components with Known Vulnerabilities: This vulnerability refers to the use of outdated or vulnerable components (such as libraries, frameworks, or plugins) that can be exploited by attackers to gain unauthorized access or execute malicious code.
    - Insufficient Logging and Monitoring: This vulnerability occurs when an application does not generate or retain sufficient logs or fails to monitor the logs effectively, making it difficult to detect and respond to security incidents.

### Django specific guidelines

Follow the Django coding style guide. [here](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/).

  - Use Django's ORM (Object-Relational Mapping) for database access and avoid writing raw SQL queries whenever possible.
  - Organize your Django project using the recommended project structure (https://docs.djangoproject.com/en/dev/intro/reusable-apps/).
  - Utilize Django's built-in security features like CSRF protection and authentication middleware.
  - Implement the principle of "Don't Repeat Yourself" (DRY) by reusing code through Django's class-based views, mixins, and template tags.

#### **Performance**:
  - Optimize database queries by using select_related() and prefetch_related() to reduce the number of database hits.
  - Use caching mechanisms (e.g., Django's caching framework or Redis) to improve performance for frequently accessed data.
  - Minimize the number of queries executed within loops or recursion.

### **Testing and Quality Assurance**:
  - Write automated tests for your Django application using Django's built-in testing framework (e.g., unit tests, integration tests, and functional tests).
  - Aim for high test coverage to ensure the correctness and stability of your code.
  - Use tools like Flake8, pylint, or mypy for static code analysis and to enforce coding standards.

### **GIT**

  - Use descriptive branch names: Choose meaningful and descriptive names for branches that indicate the purpose or feature being worked on. For example, use names like "feature/authentication" or "bugfix/user-registration" instead of generic names like "branch1" or "dev_branch."
  - Create feature branches: Each new feature or task should have its own dedicated branch. This allows for isolated development, easy collaboration, and the ability to track changes related to specific features.
  - Keep the main branch stable: The main branch (often called "master" or "main") should always contain stable and production-ready code. Avoid pushing incomplete or experimental code directly to the main branch.
  - Merge branches with pull requests: When merging code from a feature branch to the main branch, use pull requests (or merge requests) for code reviews. This helps ensure that changes are reviewed by other team members before merging them into the main branch.
  - Delete merged branches: Once a branch has been merged into the main branch or is no longer needed, delete it to keep the repository clean and avoid clutter.