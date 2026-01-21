from openrouter import Inferencer
from local import LocalLlama
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="Invoice processing CLI")
    parser.add_argument("backend", choices=["openrouter", "ollama", "llama"],
                        help="Backend to use")
    parser.add_argument("image_path", help="Path to invoice image")
    parser.add_argument("--model", type=str, default=None,
                        help="Model identifier (required for openrouter and ollama)")

    args = parser.parse_args()

    if args.backend == "llama":
        inferencer = LocalLlama()
        result = inferencer.process_invoice(args.image_path)
    else:
        if not args.model:
            print("Error: --model is required for openrouter and ollama backends",
                  file=sys.stderr)
            sys.exit(1)
        if args.backend == "openrouter":
            inferencer = Inferencer(local=False)
        else:
            inferencer = Inferencer(local=True)
        result = inferencer.process_invoice(args.image_path, args.model)

    print(result)


if __name__ == "__main__":
    main()
