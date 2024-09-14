# WeatherTrackerAPI

API to track and request weather data

## Setup Instructions

This project uses the following stack of technologies:

1. FastAPI
2. SQLAlchemy
3. OpenWeatherMap API
4. PostgreSQL

This project is containerized with a Dockerfile to build the Docker image, alongside a Docker Compose configuration for simplified environment setup.

The project contains a folder named dataset which contains an initialization script for PostgreSQL. This will populate data into the database table. If in the case that you would want to use your own database use the format for .env below and store it in the config directory:

```
API_KEY=<Your API Key>
DATABASE_URL="postgresql+asyncpg://<Postgres User>:<Postgres Password>@<Postgres Host>:<Postgres Port>/"
DATABASE_NAME="<Postgres Database Name>?<Optional query parameters>"
ECHO_SQL=<Whether to display SQL statements as logs. Accepts either True or False>
API_BASE_URL="https://api.openweathermap.org/data/3.0/onecall"
```

**Note:**
This project has been configured with OpenWeatherMap One Call subscription model. Kindly use the API Key associated to former project. <br>

To run the Docker Compose configuration, you will need an API key from OpenWeatherMap. Pass this API key as an environment variable in the Docker Compose file:

```
environment:
      - API_KEY=<Your API Key here>
```

To run the docker compose file use:

```bash
docker compose up -d
```

Link to the OpenAPI documentation: http://localhost:8000/docs

## Project structure explanation

The project follows a modular architecture, organized into separate layers for routing, models, schemas, and services. Below is the file structure:

```
.
├── Dockerfile
├── README.md
├── app
│   ├── __init__.py
│   ├── __pycache__
│   ├── config
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   └── settings.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── city_model.py
│   │   └── weather_logger_model.py
│   ├── routers
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   └── weather_router.py
│   ├── schemas
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── weather_history_schema.py
│   │   └── weather_response_schema.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   └── weather_service.py
│   └── utils
│       ├── __init__.py
│       ├── __pycache__
│       ├── database.py
│       └── exceptions.py
├── docker-compose.yml
├── requirements.txt
├── tests
│   ├── __init__.py
│   ├── __pycache__
│   ├── conftest.py
│   └── test_weather.py
└── venv

```

In the app folder we have the FastAPI application and configuration files. <br>

### Config directory

Contains application settings, managed using the `pydantic-settings` package, which automatically imports environment variables for configuration.

### Models directory

Houses the SQLAlchemy models for the database. This includes the `cities` model, which stores information such as city `name`, `latitude`, and `longitude`. The weather logger model logs each weather request, storing data such as `city_id`, `response_code`,`response_status`, `response_summary`, and the `created_at` timestamp.

Database name: `weather_app`

Schema name: `public`

#### Cities database model

Table name: `cities`

| Column Name | Description           |
| ----------- | --------------------- |
| name        | Name of the city      |
| latitude    | Latitude of the city  |
| longitude   | Longitude of the city |

#### Weather Logger database model

Table name: `weather_loggers`

| Column Name     | Description                         |
| --------------- | ----------------------------------- |
| city_id         | reference to cities.id              |
| response        | third party api response summary    |
| response_code   | third party api response code       |
| response_status | third party api response status     |
| created_at      | timestamp at which request was made |

### Routers directory

Contains all API routes, including the `weather_router.py`, which handles weather API requests and retrieves historical data.

### Schemas directory

Contains the Pydantic models used for serializing data into JSON format for API responses.

### Services directory

Implements the core business logic, including making API calls to the third-party weather service and querying historical data from the database.

### Utils directory

Contains utility modules, such as database connection management and custom exception handling.

## Exception handling

FastAPI out of the box provides with a simple HTTP exception handler. This handler requires to pass as arguments the error message and the status code. Using the same exception handler over the project structure will result in repititive code as well as difficult for other developer to read.

To solve this problem, I have employed a custom exception handler that inherits the exception handler provided by FastAPI. The naming convention followed will help the code to be more flexible and increase maintainability.

Within the project scope, the exception handler has been employed under the following principles:

1. **try-catch principle:** A simple exception handling principle that employs try and catch block within the python code to catch and handle exceptions appropriately.

   ```python
   async with AsyncClient() as client:
      try:
          response = await client.get(self.base_url, params=params)
          response.raise_for_status()
          return response

      except RequestError:
          raise ServiceError(
              message="Failed to fetch weather data",
              status_code=response.status_code,
          )
      except TimeoutException:
          raise ServiceError(
              message="Timeout fetching weather data", status_code=504
          )
   ```

2. **fail-fast principle:** An exception handling principle that stops the code from executing by catching exceptions earlier. This practice ensures that the server handles the base and edge cases earlier to prevent the system from falling.

   ```python
   city = await self.session.execute(select(City).where(City.id == city_id))
   city_in_db = city.scalar()
   if not city_in_db:
       raise EntityDoesNotExistError(message="City not found", status_code=404)
   return city_in_db
   ```

## Trade-off decisions made

An edge case arises when we are dealing with cities that are not within the preset list of cities in the database. When a request is made to fetch the current weather of that city, we will face logging issues in the database, primarily due to the fact that the city does not exist in our cities table and thus causing referrential integrity issues. Below are the ways to deal with this issue:

1. Create a foreign key in the weather logger table that refers to the cities id key. In the case when a request is made for the city that is not in the preset list, we can forgo the task to log the request in the database. This will not log issues related to `404` status code.
2. Do not create a foreign key in the weather logger table referring to the cities id primary key. In this case when a request is made we can log the `404` status code but we will lose the referrential integrity functionality.

For this assessment, I have implemented the `1st` option from the above mentioned bullet points. The reason for this is that it will improve and maintain the data consistency and data integrity within the developed system as it will prevent creating orphan records in the database.

**Note:** We need to be careful when implementing this feature and think what we would want when a record from the cities table is deleted. Would we want to delete the subsequent records in the weather logger table or not.

## Potential improvements

<p> Few of the improvements that could have been made if time permits include the following:
  <ul>
  <li>Enhance rate limiting functionality to pervent any malicious attacks. We currently use slowapi for this use case which provides a pre configured rate limiter. Proposition is to use Redis.</li>
  <li>Using alembic for database migrations. Django by default provides with migration operations but in case of FastAPI we could have used Alembic. </li>
  <li>Using background tasks to perform the logging operation. This would drastically improve the performance for the API as the FastAPI provides functionality for the same. The background tasks are performed after the response has been dispatched.</li>
  <li>Ability to add cities to the preset lists. This can be done by incorporating geolocation functionality within the app.</li>
  </ul>
</p>
