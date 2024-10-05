# AioMysql Documentation

## Required Modules

`pip install aiomysql`

## AioMysqlError

### AioMysqlError
- **Description**: Base class for AioMysql exceptions.

### ConnectionError
- **Description**: Exception raised for errors related to database connection.

### QueryError
- **Description**: Exception raised for errors during the execution of SQL queries.

### MultipleQueryError
- **Description**: Exception raised for errors during the execution of multiple SQL queries.

### TransactionError
- **Description**: Exception raised for errors related to transactions.

## AioMysql

### AioMysql
- **Description**: Class for managing asynchronous MySQL database connections and operations.

#### __init__(host: str, port: int, user: str, password: str, db: str) -> None
- **Parameters**:
  - `host`: Hostname of the MySQL server.
  - `port`: Port number of the MySQL server.
  - `user`: Username for the MySQL database.
  - `password`: Password for the MySQL database.
  - `db`: Name of the database to connect to.

#### connect() -> None
- **Description**: Creates a connection pool to the database.

#### execute_one(query: str, args: Optional[Tuple[Any, ...]] = ()) -> Tuple[int, Optional[List[Tuple[Any, ...]]]
- **Description**: Executes a SQL query and returns the number of affected rows and the result.
- **Parameters**:
  - `query`: SQL query to execute.
  - `args`: Optional parameters for the SQL query.

#### execute_change(query: str, args: Optional[Tuple[Any, ...]] = ()) -> int
- **Description**: Executes a SQL query that modifies data and returns the number of affected rows.
- **Parameters**:
  - `query`: SQL query to execute.
  - `args`: Optional parameters for the SQL query.

#### execute_select(query: str, args: Optional[Tuple[Any, ...]] = ()) -> List[Tuple[Any, ...]]
- **Description**: Executes a SQL query to select data and returns the result.
- **Parameters**:
  - `query`: SQL query to execute.
  - `args`: Optional parameters for the SQL query.

#### exec_many(query: str, args_list: List[Tuple[Any, ...]]) -> None
- **Description**: Executes the same SQL query multiple times with different sets of parameters.
- **Parameters**:
  - `query`: SQL query to execute.
  - `args_list`: List of parameter sets for the SQL query.

#### fetch_iter(query: str, *, args: Optional[Tuple[Any, ...]] = (), batch_size: int = 100) -> AsyncIterator[Tuple[Any, ...]]
- **Description**: Asynchronous iterator for fetching data in batches.
- **Parameters**:
  - `query`: SQL query to execute.
  - `args`: Optional parameters for the SQL query.
  - `batch_size`: Number of rows to fetch at a time.

#### close() -> None
- **Description**: Closes the connection pool.

## Transaction

### Transaction
- **Description**: Class for managing database transactions.

#### __init__(pool: aiomysql.Pool) -> None
- **Parameters**:
  - `pool`: Connection pool to be used for the transaction.

#### begin() -> None
- **Description**: Starts a transaction.

#### execute(query: str, args: Optional[Tuple[Any, ...]] = ()) -> Tuple[int, Optional[List[Tuple[Any, ...]]]
- **Description**: Executes a SQL query within the current transaction.
- **Parameters**:
  - `query`: SQL query to execute.
  - `args`: Optional parameters for the SQL query.

#### commit() -> None
- **Description**: Commits the current transaction.

#### rollback() -> None
- **Description**: Rolls back the current transaction.

#### close() -> None
- **Description**: Closes the connection used in the transaction.
