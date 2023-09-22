# Unipi Library  Web Application

[![Python3](https://img.shields.io/badge/language-Python3-red)](https://img.shields.io/badge/language-Python3-red)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://img.shields.io/badge/Docker-Supported-blue)
![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)

Unipi's Library Web application is a web application which contains the most important functionalities of a library system renting books. 
In more details there are two types of users in the App: Users and Administrators. Administrators have the role to maintain integrity and fully updated the database.
Users on the other hand are the main users of the Web application.

## Endpoints

This web application contains endpoints to provide access in the utilities for both types of users.

### Administrators

The endpoints below refers to the functionalities of administrators:

```text
- /                             Choose the type of user
- /admin/loginAdmin             Login an administrator to the system (hard coded credentials)
- /admin/insertBook           Insert a new book into the database
- /admin/deleteBook           Delete an existing book from the database
- /admin/adminSearchBook            Searching for books in the database    
- /admin/logout                 Logout the administrator from the system
```

You can find detailed usage of the above endpoints [here](doc/adminEndpoints.md).

### Users

The endpoints below contains functionalities of application's simple users

```text
- /                                      Choose the type of user
- /user/login                            Login a User to the system
- /user/registerUser                     Register a User to the system
- /user/searchBook                       Search for book with specified criteria
- /user/rentBook                         Rent a book from the available ones
- /user/viewBookings                     View bookings with booking number
- /user/returnBook                       Return book with booking number
- /user/deactivateAccount                Delete User's account
- /user/logout                           Logout the user from the system
```

You can find detailed usage of the above endpoints [here](doc/userEndpoints.md).

## Instalation

1. Fork/Clone/Download this repo

   `git clone [yourRepoName]`

2. Navigate to the directory

   `cd app`

3. Run the command bellow

   `docker compose up --build -d`

Note: Docker should be installed in the system
