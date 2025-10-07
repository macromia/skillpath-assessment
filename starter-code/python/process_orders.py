import argparse

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--threshold', type=float, default=100.0)
    return p.parse_args()

if __name__ == '__main__':
    args = parse_args()
    # TODO: read CSV, build Order objects, compute analytics, write outputs