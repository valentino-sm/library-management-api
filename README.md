+ Register, log in, and access the API using API tokens.
+ Differentiate between regular users and administrators with additional privileges.
+ Regular users can view and search on the basis of the book details. 
+/- As for admins, they are able to create users, change membership status and manage what categories of books are available for a certain user(default all categories).

+ Implement data models for books, authors, and library members.
+ Books should have attributes such as title, author, language, publication date, category and ISBN(10-digit ISBN).
+ Library members should have attributes such as name, contact information, permissions and membership status(ACTIVE, BLOCKED), membership period.

+ Integrate with an external book information GB API (Google Books API) to fetch books' details like title, author, language, publication date, ISBN.
+ The details retrieved from GB API must be stored in a local DB for further queries similar requests. 
+ Users should be able to get: books details by ISBN, books by categories.  
+ Cache the API responses using Redis for better performance.

+ Implement an advanced search endpoint allowing users to search for books based on various criteria, such as title, author, publication date, or ISBN.
- Create 50% coverable Test cases followin TDD best practices. 

# Simple Library Management API

#### Docker
Set GOOGLE_API_KEY in environment variables.
```sh
docker compose up
```

#### Usage
[Go to Swagger API Docs](http://localhost:8000/docs)


#### Not for production.
