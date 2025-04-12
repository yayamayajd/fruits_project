# Difficulties and Solutions

to be continued...

## 🔍 Testing: Transactions + Savepoint

I primarily used pytest to test my routes, focusing on a mix of unit tests and partial integration tests.

The main testing method involved using assert statements to verify that, after performing CRUD operations via specific functions, the response status codes were as expected and redirects were working correctly.

To isolate the test data and avoid polluting the actual database, I used database transactions during testing. I set up a dedicated test database with hardcoded (stubbed) test data. Through this process, I learned what a transaction is and how it should be properly used in a test environment.

In this context, transactions are used to isolate data changes between tests. I implemented this using transactions + savepoints with SQLAlchemy’s begin_nested() method, which allowed me to roll back the database to a clean state after each test.

Within the CI/CD pipeline, I used a test-specific database to avoid exposing sensitive data from the production environment. Test data was manually inserted into the test database using hardcoded stubs.

Before each test run, I manually cleared the test database and reset the fruit_id and review_id sequences. This was necessary because using transactions alone would sometimes raise the following error:

```python
sqlalchemy.exc.IntegrityError: (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint
```

In addition, I avoided calling commit() within tests, as doing so would finalize the transaction and prevent proper rollback.


During my retrospectives, I realized that I could have used mocking to simplify database-related tests, especially for pure unit tests that do not involve real database behaviors such as transactions, concurrency, or locks. I plan to explore mocking strategies further in the future.

### 🧩 Other Issues
Due to the cluttered project root directory, I moved app.py and model.py into a new app/ folder. However, this caused the app to fail to locate the correct entry point. After adjusting the setup, I was able to run the application successfully using app.app as the entry point.


## 🔍 Problems Caused by Not Using a RESTful Design — and How Hard It Was to Troubleshoot

When I designed the fruit management system, my goal was to build it using the tech stack I had already learned, while also preparing for DevOps-related tools I would use later. To keep the system minimal, I chose Flask as the framework, used Python for the backend, and Jinja templates to render the frontend.

At first, everything seemed fine. The pages loaded correctly, and the backend interacted with the database as expected. But the real issue emerged during testing.

I wrote tests for each backend function and used assertions to check the returned status codes. At the time, I thought I was writing unit tests — but later, as I learned more about testing, I realized that I was actually performing integration tests, since the frontend and backend were tightly coupled.

After a long cycle of revisions and repeated test runs, all results came back green. This suggested that there were no logic errors.
But when I manually checked the application, something odd happened: one test was supposed to delete a comment related to a fruit. The test passed, but the comment was still there — and worse, a different fruit next to it in the list had disappeared.

I was completely confused.

I reviewed the test code again but couldn’t spot anything wrong. Then I went back to the backend logic — still nothing wrong there.
Could it be a database relationship issue? I reviewed the relationship tables and manually tested them again and again. I initially suspected the issue was with the use of backref, so I switched to back_populates, but no matter how I modified the relationships, the problem persisted: deleting a comment caused the wrong fruit to disappear.

This issue blocked me for quite some time. I simply couldn’t find the root cause.

Then, I had a sudden insight — what if the issue was in the frontend?
Because the project wasn’t built on a separated frontend-backend architecture, the HTML templates actually participated in backend logic.

Following this new direction, I finally located the bug:
In the fruit detail page template, I had several <form> elements connected to different backend functions.
But due to a naming mistake in the HTML, two forms ended up using the same function name or endpoint by accident.
As a result, when the test code triggered the action to delete a comment, it actually called the wrong route, and deleted a completely unrelated fruit instead.

This debugging process taught me something I’ll never forget:
Not separating the frontend from the backend adds massive complexity to both testing and troubleshooting.
From that moment, I made a clear decision: in version 2.0, the frontend and backend will be fully decoupled.