import argparse
from bloch_tools import plot_bloch_dual

def main():
    parser = argparse.ArgumentParser(description="Q-OS Tricorder")
    parser.add_argument("--bloch", nargs=2, type=float, metavar=("THETA","PHI"),
                        help="Render Bloch-Sphere (Innen/Außen) für (theta,phi) in Radiant")
    args = parser.parse_args()
    if args.bloch:
        theta, phi = args.bloch
        print(f"[Q-OS] Rendering Bloch-Sphere for θ={theta}, φ={phi}")
        plot_bloch_dual(theta, phi, save_as="bloch_inside_outside.mp4")

if __name__ == "__main__":
    main()
