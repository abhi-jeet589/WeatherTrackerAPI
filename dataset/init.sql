CREATE TABLE IF NOT EXISTS weather_app.public.cities (
  id SERIAL NOT NULL,
  name VARCHAR(100) NOT NULL,
  latitude FLOAT NOT NULL,
  longitude FLOAT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (name)
);

INSERT INTO weather_app.public.cities VALUES (1, 'Calgary', 51.04, -114.06);

CREATE TABLE IF NOT EXISTS weather_loggers (
        id SERIAL NOT NULL,
        city_id INTEGER NOT NULL,
        response_code INTEGER NOT NULL,
        response_status VARCHAR(20) NOT NULL,
        response TEXT NOT NULL,
        created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(city_id) REFERENCES cities (id)
)