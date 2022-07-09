#!/usr/bin/env python
"""
Performs basic cleaning on the data and save the results in Weights & Biases
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()


def go(args):

    run = wandb.init(job_type="basic_cleaning")
    # run.config.update(args)

    logger.info("Downloading data artifact")
    artifact = run.use_artifact(args.input_artifact)
    artifact_path = artifact.file()

    df = pd.read_csv(artifact_path)

    logger.info("Dropping outliers below 5 percentile and above 95 percentile")
    # Retrieve min and max price from parameter
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Set the boundaries for longitude and latitude
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    df.to_csv("clean_sample.csv", index=False)

    logger.info("Saving artifact")
    artifact = wandb.Artifact(
        args.artifact_name,
        type=args.artifact_type,
        description=args.artifact_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="This steps cleans the data")


    parser.add_argument(
        "--input_artifact", 
        type=str,
        help="Path to the input file",
        required=True
    )

    parser.add_argument(
        "--artifact_name", 
        type=str,
        help="Name for the artifact",
        required=True
    )

    parser.add_argument(
        "--artifact_type", 
        type=str,
        help="Type for the artifact",
        required=True
    )

    parser.add_argument(
        "--artifact_description", 
        type=str,
        help="Description of the artifact",
        required=True
    )

    parser.add_argument(
        "--min_price", 
        type=float,
        help="Minimum price",
        required=True
    )

    parser.add_argument(
        "--max_price", 
        type=float,
        help="Maximum price",
        required=True
    )


    args = parser.parse_args()

    go(args)
