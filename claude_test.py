# import os
from anthropic import Anthropic

anthropic = Anthropic(
    api_key='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'
)
def main():    
    while True:
        prompt = input("Ask a question: (type 'exit' to quit): ")

        if prompt.lower() == "exit":
            print("Goodbye!")
            break

        try:
            message = anthropic.messages.create(
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model="claude-3-5-sonnet-latest",
            )
            print(message.content[0].text)
        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
