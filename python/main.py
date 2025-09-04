import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config("app.api:app", host="127.0.0.1", port=8001, reload=True)
    server = uvicorn.Server(config)
    server.run()