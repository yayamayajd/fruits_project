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

