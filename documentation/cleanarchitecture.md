## What is clean architecture in Django?

Clean Architecture in the context of Django web applications is an architectural pattern 
that emphasizes the separation of concerns and the independence of the core business logic from the web framework and other external dependencies. It aims to create a modular and maintainable codebase for web applications that is flexible, testable, and scalable.

Benefits of applying Clean Architecture principles in Django web applications include:

-&nbsp; **Modularity and Maintainability** By separating the core business logic from the web framework, Clean Architecture promotes modularity and maintainability. Changes in the web framework or user interface do not impact the core domain logic, making it easier to evolve and maintain the codebase over time.

-&nbsp; **Testability**: Clean Architecture enables easier testing of the core business logic by isolating it from external dependencies. Business rules and use cases can be thoroughly tested without relying on the web framework or other infrastructure components, leading to more reliable and robust tests.

-&nbsp; **Flexibility and Adaptability**: The clean separation of concerns and the independence from external frameworks provide flexibility and adaptability. It becomes easier to switch or upgrade the web framework, integrate with different third-party services or APIs, or even transition to different deployment environments.

-&nbsp; **Scalability**: Clean Architecture promotes the creation of loosely coupled components and clearly defined boundaries between layers. This makes it easier to scale the application by introducing additional infrastructure components or splitting functionalities into microservices without impacting the core business logic.

-&nbsp; **Reduced Technical Debt**: By following Clean Architecture principles, the codebase is structured in a way that minimizes technical debt. The separation of concerns and the clear organization of modules make the codebase easier to understand and maintain, reducing the accumulation of unnecessary complexity over time.

-&nbsp; **Focus on Domain Logic**: Clean Architecture encourages a focus on the core domain logic and business rules of the web application. The separation of the core domain from the web framework allows developers to concentrate on modeling the problem domain effectively and implementing the core features without being constrained by the specifics of the web framework.
By adopting Clean Architecture in Django web applications, developers can achieve a codebase that is more modular, maintainable, testable, and adaptable. The architecture helps in creating web applications with a clear separation of concerns, a focus on business logic, and the ability to evolve and scale as the application requirement


## Example of project structure

```commandline
rh/
├── core/
│   ├── entities/
│   │   ├── __init__.py
│   │   └── models.py         # Domain models or entities
│   ├── usecases/
│   │   ├── __init__.py
│   │   ├── create_organisations.py   # Use case implementation
│   │   └── get_organisations.py   # Use case implementation
│   └── interfaces/
│       ├── __init__.py
│       └── repositories.py    # Repository interfaces
├── repositories/
│   ├── __init__.py
│   └── organisations_repository.py   # Repository implementation
├── interfaces/
│   ├── __init__.py
│   └── web/
│       ├── __init__.py
│       ├── controllers.py     # Controllers or API handlers
│       └── rh/                # Django app (RH)
│           ├── __init__.py
│           ├── models.py      # Django models
│           ├── views.py       # Django views or viewsets
│           ├── serializers.py # Django serializers
│           └── urls.py        # Django app URLs
└── settings.py
```

- **rh**: This is the main directory representing the root of your Django project. It contains all the code and configuration related to the "RH" web application.


- **core**: This directory contains the core business logic of the application. It encapsulates the most essential components of the application's domain.

  - **entities**: This subdirectory holds the domain models or entities. These models represent the core concepts and entities of your application's domain. Entities are typically implemented as classes or data structures that contain attributes and methods related to the domain-specific data and behaviors.
  - **usecases**: Here, you'll find the implementations of the use cases or application-specific operations. Each use case represents a specific action or workflow of your application. Examples include creating a new object or removing it.
  - **interfaces**: This subdirectory includes the repository interfaces that define the contracts for data access and persistence in the core. These interfaces serve as a bridge between the core and the repositories. 


- **repositories**: The repositories directory contains the implementations of the repository interfaces defined in the core.interfaces package. The organisation_repository.py file represents a repository implementation responsible for handling data access and persistence operations for organisations.
- **interfaces**: This directory represents the web interface layer of your application, specifically for the web-based part of the app. 
  - **web**: The web subdirectory contains the code related to the web interface layer.
    - **controllers**: The controllers.py file holds the controllers or API handlers responsible for handling requests and responses in the web interface layer. It acts as an intermediary between the web framework and the core use cases.
    - **rh**: This subdirectory represents the Django app named "RH" within the web interface layer.
    - **models**: The models.py file contains the Django models that define the data structure and relationships for the "RH" app.
    - **views**: The views.py file holds the Django views or viewsets that handle the logic for rendering templates or handling API requests for the "RH" app.
    - **serializers**: The serializers.py file defines the serializers for the Django models in the "RH" app. Serializers are used for converting complex data structures, such as models, into JSON or other formats.
    - **urls**: The urls.py file contains the URL configuration for the "RH" app, mapping URLs to the corresponding views or viewsets.


- **settings.py**: This file represents the Django project's settings file, which includes various configurations for the project.