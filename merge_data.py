import os
import json
import pandas as pd

def flatten_audio_features(audio_data: dict) -> dict:
    """
    Given a dictionary of audio features (parsed from JSON),
    produce a flattened dictionary suitable for adding as columns
    in the main DataFrame.
    """
    flat = {}
    
    # --- Basic top-level fields ---
    flat["tempo"] = audio_data.get("tempo", None)
    flat["danceability"] = audio_data.get("danceability", None)
    flat["key"] = audio_data.get("key", None)
    flat["duration"] = audio_data.get("duration", None)
    
    # --- Single 'stats' dictionaries (same structure) ---
    # For example: chroma_stft_stats, spectral_centroid_stats, zero_crossing_rate_stats, rms_stats.
    # Each has keys: mean, variance, median, skewness, kurtosis, min, max.
    
    for stats_name in [
        "chroma_stft_stats",
        "spectral_centroid_stats",
        "zero_crossing_rate_stats",
        "rms_stats"
    ]:
        stats_dict = audio_data.get(stats_name, {})
        if isinstance(stats_dict, dict):
            for k, v in stats_dict.items():
                flat[f"{stats_name}_{k}"] = v
        else:
            # If something is missing or unexpected, store None for each possible sub-field
            for k in ["mean", "variance", "median", "skewness", "kurtosis", "min", "max"]:
                flat[f"{stats_name}_{k}"] = None
    
    # --- MFCC stats: an array of length 20, each with mean/variance/etc. ---
    # We'll name columns like mfcc_stats_0_mean, mfcc_stats_0_variance, ...
    mfcc_array = audio_data.get("mfcc_stats", [])
    if isinstance(mfcc_array, list) and len(mfcc_array) > 0:
        for i, mfcc_obj in enumerate(mfcc_array):
            for k, v in mfcc_obj.items():
                flat[f"mfcc_stats_{i}_{k}"] = v
    else:
        # Store empty (None) columns if not present
        for i in range(20):
            for k in ["mean","variance","median","skewness","kurtosis","min","max"]:
                flat[f"mfcc_stats_{i}_{k}"] = None
    
    # --- Spectral contrast stats: array of length 7, each with mean/variance/etc. ---
    spec_contrast_array = audio_data.get("spectral_contrast_stats", [])
    if isinstance(spec_contrast_array, list) and len(spec_contrast_array) > 0:
        for i, contrast_obj in enumerate(spec_contrast_array):
            for k, v in contrast_obj.items():
                flat[f"spectral_contrast_stats_{i}_{k}"] = v
    else:
        for i in range(7):
            for k in ["mean","variance","median","skewness","kurtosis","min","max"]:
                flat[f"spectral_contrast_stats_{i}_{k}"] = None
    
    # --- Tonnetz stats: array of length 6, each with mean/variance/etc. ---
    tonnetz_array = audio_data.get("tonnetz_stats", [])
    if isinstance(tonnetz_array, list) and len(tonnetz_array) > 0:
        for i, ton_obj in enumerate(tonnetz_array):
            for k, v in ton_obj.items():
                flat[f"tonnetz_stats_{i}_{k}"] = v
    else:
        for i in range(6):
            for k in ["mean","variance","median","skewness","kurtosis","min","max"]:
                flat[f"tonnetz_stats_{i}_{k}"] = None

    return flat


def find_json_path(row, base_audio_folder="audio"):
    """
    Decide how to find the corresponding JSON file for the given row in contestants.csv.
    This is a placeholder logic; adjust it as needed based on how you store or name the JSON files.
    For instance, it could involve 'year', 'to_country_id', 'performer', or some standardized naming convention.
    """
    # Example of constructing a path based on year and country code (and maybe performer).
    # In practice, adapt to your actual JSON filenames and folder structure.
    year_str = str(int(row["year"]))
    country = row["to_country"].replace("?", "#").replace("/", "#").replace('\\', "#").replace("<", "#").replace(">", "#").replace('"', "#").replace("|", "#").replace("*", "#").replace(":", "#")
    performer = row["performer"].replace("?", "#").replace("/", "#").replace('\\', "#").replace("<", "#").replace(">", "#").replace('"', "#").replace("|", "#").replace("*", "#").replace(":", "#")
    song = row["song"].replace("?", "#").replace("/", "#").replace('\\', "#").replace("<", "#").replace(">", "#").replace('"', "#").replace("|", "#").replace("*", "#").replace(":", "#")
    
    # You might store the JSON in a subfolder named after the year:
    # e.g. audio/1956/Switzerland_Lys Assia.json
    # or any other pattern you have in your dataset
    json_filename = f"{country}_{song}_{performer}.json"
    json_path = os.path.join(base_audio_folder, year_str, json_filename)
    
    if os.path.exists(json_path):
        return json_path
    else:
        return None


def main():
    # 1. Read the contestants CSV
    df = pd.read_csv("contestants.csv", dtype=str).fillna("")
    
    # 2. Prepare columns for new audio features (we will store them here)
    audio_features_list = []
    
    for idx, row in df.iterrows():
        # 3. Locate the corresponding JSON file
        json_file_path = find_json_path(row)
        
        if json_file_path and os.path.isfile(json_file_path):
            # 4. Load and flatten the JSON
            with open(json_file_path, "r", encoding="utf-8") as f:
                audio_data = json.load(f)
            flat_data = flatten_audio_features(audio_data)
        else:
            # If no JSON found, create an all-None dictionary with same keys
            empty_audio_data = {}
            # We can just use flatten_audio_features({}) or replicate the structure
            # to produce None for all fields
            flat_data = flatten_audio_features(empty_audio_data)
        
        audio_features_list.append(flat_data)
    
    # 5. Convert the list of dicts to a DataFrame and merge with the original
    audio_features_df = pd.DataFrame(audio_features_list)
    merged_df = pd.concat([df, audio_features_df], axis=1)
    
    # 6. Write out the enriched DataFrame
    merged_df.to_csv("contestants_with_audio_features.csv", index=False)
    print("Successfully created contestants_with_audio_features.csv.")

if __name__ == "__main__":
    main()
