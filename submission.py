import argparse
from pathlib import Path

from src.document_pipeline import extract_text_from_pdf


def main(args: argparse.Namespace):
    """Write the entrypoint to your submission here"""
    if not args.path_to_case_pdf:
        raise AttributeError("Please provide a path to a PDF using --path-to-case-pdf <file path>")
    # TODO - import and execute your code here. Please put business logic into repo/src
    data = extract_text_from_pdf(Path(args.path_to_case_pdf))
    print(data.to_string())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path-to-case-pdf',
                        metavar='path',
                        type=str,
                        help='Path to local test case with which to run your code')
    args = parser.parse_args()
    main(args)
