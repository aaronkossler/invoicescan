from backend import Backend, BackendType
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Invoice processing CLI")
    parser.add_argument("backend", type=BackendType, choices=list(BackendType),
                        help="Backend to use")
    parser.add_argument("image_path", help="Path to invoice image")
    parser.add_argument("--model", help="Model (required for openrouter/ollama)")

    args = parser.parse_args()

    backend = Backend(type=args.backend, model=args.model)

    if args.backend == BackendType.LLAMA:
        result = backend.process_invoice(args.image_path)
    else:
        if not args.model:
            print("Error: --model is required for openrouter and ollama", file=sys.stderr)
            sys.exit(1)
        result = backend.process_invoice(args.image_path, args.model)

    print(result)


if __name__ == "__main__":
    main()
