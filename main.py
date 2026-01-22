from backend import Backend, BackendType
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Invoice processing CLI")
    parser.add_argument("backend", type=BackendType, choices=list(BackendType),
                        help="Backend to use")
    parser.add_argument("image_path", help="Path to invoice image")
    parser.add_argument("--model", help="Model (required for openrouter/ollama)")
    parser.add_argument("--url", default="http://localhost:8080/v1",
                        help="Server URL for llama backend (default: http://localhost:8080/v1)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable detailed debug output")

    args = parser.parse_args()

    try:
        backend = Backend(type=args.backend, base_url=args.url, model=args.model)

        if args.debug:
            print(f"Connecting to {args.url}")
            print(f"\n--- Testing invoice detection on: {args.image_path} ---")

        result = backend.invoice_or_not(args.image_path)

        if args.debug:
            print(f"Result: {result}")

        invoice_data = json.loads(result)

        if invoice_data.get("invoice"):
            if args.debug:
                print("\n--- Invoice detected! Extracting properties ---")

            properties = backend.invoice_properties(args.image_path)

            if args.debug:
                print(f"Properties: {properties}")

            props_data = json.loads(properties)

            if args.debug:
                print("\n--- Extracted Data ---")
                print(f"Date: {props_data.get('invoice_date')}")
                print(f"Total: {props_data.get('total_amount')}")
                print(f"Currency: {props_data.get('currency')}")

            print(json.dumps(props_data))
        else:
            if args.debug:
                print("Image is not an invoice.")
            print(json.dumps({"invoice": False}))

    except FileNotFoundError:
        print(f"Error: Could not find file '{args.image_path}'", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON response: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
