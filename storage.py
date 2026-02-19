#Analysis result comes from analyzer.py
#        ↓
#storage.py saves it to data/results.csv
#        ↓
#Recruiter can view, filter, sort history
#        ↓
#Recruiter can add notes or delete a candidate
import pandas as pd
import os
from datetime import datetime

# Section 2 — Setting up the CSV file.
# Path to the CSV file
DATA_FOLDER = "data"
CSV_FILE = "data/results.csv"

# Columns in the CSV file
COLUMNS = [
    "candidate_name",
    "experience_level",
    "overall_score",
    "verdict",
    "verdict_reason",
    "matched_skills",
    "missing_skills",
    "red_flags",
    "strengths",
    "summary",
    "score_reason",
    "notes",
    "date_analyzed"
]

def initialize_storage():
    # Create data folder if it doesn't exist
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    
    # Create CSV file if it doesn't exist
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, index=False)

#Section 3 — Saving a new candidate result.
def save_result(result):
    # Load existing data
    df = pd.read_csv(CSV_FILE)
    
    # Create a new row from the result
    new_row = {
        "candidate_name": result.get("candidate_name", "Unknown"),
        "experience_level": result.get("experience_level", ""),
        "overall_score": result.get("overall_score", 0),
        "verdict": result.get("verdict", ""),
        "verdict_reason": result.get("verdict_reason", ""),
        "matched_skills": ", ".join(result.get("matched_skills", [])),
        "missing_skills": ", ".join(result.get("missing_skills", [])),
        "red_flags": ", ".join(result.get("red_flags", [])),
        "strengths": ", ".join(result.get("strengths", [])),
        "summary": result.get("summary", ""),
        "score_reason": result.get("score_reason", ""),
        "notes": "",
        "date_analyzed": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # Add new row to dataframe
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save back to CSV
    df.to_csv(CSV_FILE, index=False)

#Section 4 — Reading and filtering candidates! 
    def load_results():
    # Return empty dataframe if file doesn't exist
        if not os.path.exists(CSV_FILE):
            return pd.DataFrame(columns=COLUMNS)
    
        # Load and return the CSV data
        df = pd.read_csv(CSV_FILE)
        return df

    def filter_results(df, verdict=None, min_score=0, max_score=100):
        # Filter by verdict if provided
            if verdict and verdict != "All":
                df = df[df["verdict"] == verdict]
        
# Filter by score range
            df = df[
            (df["overall_score"] >= min_score) & 
            (df["overall_score"] <= max_score)
            ]
            return df

    def sort_results(df, sort_by="overall_score", ascending=False):
            # Sort the dataframe by given column
            if sort_by in df.columns:
                df = df.sort_values(by=sort_by, ascending=ascending)
            return df

#Section 4 — Reading and filtering candidates.
def load_results():
            # Return empty dataframe if file doesn't exist
            if not os.path.exists(CSV_FILE):
                return pd.DataFrame(columns=COLUMNS)
            
            # Load and return the CSV data
            df = pd.read_csv(CSV_FILE)
            return df

def filter_results(df, verdict=None, min_score=0, max_score=100):
            # Filter by verdict if provided
            if verdict and verdict != "All":
                df = df[df["verdict"] == verdict]
            
            # Filter by score range
            df = df[
                (df["overall_score"] >= min_score) & 
                (df["overall_score"] <= max_score)
            ]
            
            return df

def sort_results(df, sort_by="overall_score", ascending=False):
            # Sort the dataframe by given column
            if sort_by in df.columns:
                df = df.sort_values(by=sort_by, ascending=ascending)
            return df

#Section 5 — Adding notes and deleting candidates.
def update_notes(candidate_name, date_analyzed, notes):
    # Load existing data
    df = pd.read_csv(CSV_FILE)
    
    # Find the candidate row and update notes
    mask = (
        (df["candidate_name"] == candidate_name) & 
        (df["date_analyzed"] == date_analyzed)
    )
    df.loc[mask, "notes"] = notes
    
    # Save back to CSV
    df.to_csv(CSV_FILE, index=False)

def delete_candidate(candidate_name, date_analyzed):
    # Load existing data
    df = pd.read_csv(CSV_FILE)
    
    # Remove the candidate row
    df = df[~(
        (df["candidate_name"] == candidate_name) & 
        (df["date_analyzed"] == date_analyzed)
    )]
    
    # Save back to CSV
    df.to_csv(CSV_FILE, index=False)
