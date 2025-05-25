import argparse
from aiqtoolkit import AIQ, load_yml_config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config.yml")
    parser.add_argument("--query", help="Cybersecurity question")
    args = parser.parse_args()

    config = load_yml_config(args.config)
    aiq = AIQ(config)

    if args.query:
        response = aiq.run(args.query)
        print(f"Final Answer with Citations:\n{response}")
    else:
        print("Interactive mode. Type 'exit' to quit.")
        while True:
            query = input("Query: ")
            if query.lower() == "exit":
                break
            response = aiq.run(query)
            print(f"Final Answer with Citations:\n{response}")

if __name__ == "__main__":
    main()
