import argparse
import uvicorn

def main() -> None:
    parser = argparse.ArgumentParser(prog="naviqra")
    parser.add_argument("command", choices=["serve"], nargs="?", default="serve")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run("naviqra.api:app", host=args.host, port=args.port, reload=False)

if __name__ == "__main__":
    main()
