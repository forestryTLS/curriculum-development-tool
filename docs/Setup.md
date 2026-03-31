# 🛠️ Project Setup Guidelines

## Requirements

- PHP
- Composer
- Laravel
- Node.js and npm
- PostgreSQL
- Python

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

### Storage Setup

```
php artisan storage:link
```

### Run migrations and seeders

```
php artisan migrate --seed
```

### Run the Application

Start the queue worker by running the following command:

``` 
php artisan queue:work
```

Run the application locally with the following command:
```
php artisan serve
```
Access the application at [http://localhost:8000](http://localhost:8000)

### Running Tests

```
php artisan test 
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