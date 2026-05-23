from fastapi import FastAPI
from app.api.upload import router

app = FastAPI()

app.include_router(router)

def main():
    print("Hello from legal-doc-qa!")


if __name__ == "__main__":
    main()
