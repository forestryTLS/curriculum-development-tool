# 🛠️ Project Setup Guidelines

## Requirements

- PHP `^8.2`
- Composer
- Laravel 10
- Node.js and npm
- PostgreSQL
- Python (for running the microservices under `python/services/`)

### Clone this repository

```
git clone https://github.com/forestryTLS/curriculum-development-tool.git
cd curriculum-development-tool
```

## Laravel Setup

### Install Dependencies

```
cd laravel
composer install
npm install
```

### Environment Setup

```
cp .env.example .env
```

### Application Key

```
php artisan key:generate
```

### Database Setup

#### Initialize a PostgreSQL cluster (one-time, only if not already done)

Check whether you already have a PostgreSQL cluster set up and running:

```
psql -U postgres -l
```

If you see a table of databases (`postgres`, `template0`, `template1`), the cluster is initialized and running. Skip ahead to **Create the application database**.

If you see `psql: could not connect to server`, the cluster either has not been created or is not running. Pick a directory to hold the cluster data (substitute your own path), then:

```
initdb -D <path-to-data-directory> --username=postgres
pg_ctl -D <path-to-data-directory> start
```

To stop the server later, use `pg_ctl -D <path-to-data-directory> stop`.

If you see `psql: command not found`, PostgreSQL is not installed; install it first.

#### Create a `root` role (if your `.env` uses `DB_USERNAME=root`)

If your `.env` uses `postgres` as the user, you can skip this step.

The `postgres` superuser is created during `initdb`, but `root` is not. If your `.env` is set to `DB_USERNAME=root` (the project default), create that role once:

```
psql -U postgres -h 127.0.0.1 -c "CREATE ROLE root LOGIN PASSWORD '';"
```

Adjust the password to match `DB_PASSWORD` in your `.env`.

#### Create the application database

```
psql -U postgres -h 127.0.0.1 -c "CREATE DATABASE laravel OWNER root;"
```

Replace `laravel` and `root` with whatever you have in `DB_DATABASE` and `DB_USERNAME` in your `.env`.


### Storage Setup

```
php artisan storage:link
```

### Run migrations and seeders

```
php artisan migrate --seed
```

### Front-end Assets

The project uses Vite for SCSS compilation and JavaScript bundling. Two workflows are available:

**Development (with hot reload)**:

```
npm run dev
```

Vite starts a dev server on `http://localhost:5173/` and serves assets with hot module replacement.

**Production build**:

```
npm run build
```

Compiles a static bundle into `public/build/`. Use this for deployments or when you want to run the app without the dev server.

Both commands trigger a `prebuild`/`predev` hook that copies jQuery into `public/vendor/` (the same copy described in **Install Dependencies**). You do not need to run anything separately.

### Run the Application

Start the queue worker in one terminal:

``` 
php artisan queue:work
```

Run the application in another:

```
php artisan serve
```

Access the application at [http://localhost:8000](http://localhost:8000). If you want hot-reloading front-end assets while developing, also start the Vite dev server in a third terminal with `npm run dev`.

### Running Tests

The project uses a separate `.env.testing` file and a dedicated test database so that running tests don't interfere with the development/production data.

**First-time setup**:

1. Create a separate test database. Replacing `laravel_test` and `root` to match your .env.testing setup:

   ```
   psql -U postgres -h 127.0.0.1 -c "CREATE DATABASE laravel_test OWNER root;"
   ```

2. Copy the test environment template and edit as needed:

   ```
   cp .env.testing.example .env.testing
   ```

   The committed template defaults to `DB_DATABASE=laravel_test` and `pgsql` on `127.0.0.1:5432`. Adjust if your local Postgres configuration differs.

3. Generate a separate app key for the testing environment:

   ```
   php artisan key:generate --env=testing
   ```

**Running the test suite**:

```
composer test
```

## Python Setup

From the project root, run `cd python` to enter the `python` directory.
If you are currently in the `laravel` directory, first run `cd ..` and then `cd python`.

### Navigate to a service
From the project `python` directory:

``` 
cd services/<service_name>
```

### Activate virtual environment

#### Unix

``` 
python3 -m venv env
source env/bin/activate
```

#### Windows

``` 
python -m venv env
.\env\Scripts\activate
```

### Install Dependencies

``` 
pip install -r requirements.txt
```

### Run the Service

``` 
python3 -m app.main 
```
