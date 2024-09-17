import argparse
import logging
from config import Config
from clip_analyzer import CLIPAnalyzer
from llm_analyzer import LLMAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Analyze images using LLM.")
    parser.add_argument("image_path", type=str, help="Path to the image file.")
    parser.add_argument("--prompt", type=str, help="The prompt to be used for analysis.")
    parser.add_argument("--model", type=int, required=True, help="Model number for analysis (1-5).")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config = Config()

    logging.info("### Processing New Batch ###")

    if config.clip_enabled:
        logging.info("Running CLIP Analyzer...")
        clip_analyzer = CLIPAnalyzer(config)
        clip_analyzer.process_images()

    if config.enable_llm_analysis:  # Check if LLM analysis is enabled
        logging.info("Running LLM Analyzer...")
        llm_analyzer = LLMAnalyzer(config)
        llm_analyzer.process_images(args.image_path, args.prompt, args.model)  # Pass the model number

    logging.info("Finished processing")

if __name__ == "__main__":
    main()