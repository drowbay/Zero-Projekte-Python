from openai import OpenAI
client = OpenAI()
while True:
    user = input("Du> ").strip()
    if not user:
        continue
    if user.lower() in {"exit", "quit"}:
        break
    resp = client.responses.create(
        model="gpt-5",
        input=user
    )
    print("Lumora>", resp.output_text)
