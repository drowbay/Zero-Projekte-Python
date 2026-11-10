from lumye.ki_module import respond

def banner():
    print("\n🌙 Lumÿè-OS / KI + isa_pi — v0.1")
    print("================================")
    print("Tippe 'help' für Befehle.\n")

def main():
    banner()
    while True:
        try:
            user = input("Du> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye 👋")
            break

        out = respond(user)
        if out == "__EXIT__":
            print("Bye 👋")
            break
        print(out)

if __name__ == "__main__":
    main()
