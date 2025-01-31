"""Main functions that run the performance marketing brain using FastAPI and LLM"""

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import json
from enum import Enum

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Performance Marketing Brain",
    description="AI-powered performance marketing analysis system",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class MarketingDataAnalysisRequest(BaseModel):
    marketing_data_meta: UploadFile | None = None
    marketing_data_google: UploadFile | None = None
    marketing_data_tiktok: UploadFile | None = None


class MarketingDataAnalysisResponse(BaseModel):
    pass


class CampaignType(Enum):
    META = "META"
    GOOGLE = "GOOGLE"
    TIKTOK = "TIKTOK"

# Endpoints
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analyze-campaigns")
async def analyze_campaigns(campaign_type: CampaignType, file1: UploadFile = File(...), file2: UploadFile = File(...)) -> dict:
    try:
        # Read the CSV files directly from the uploaded file objects
        contents1 = await file1.read()
        df1 = pd.read_csv(pd.io.common.BytesIO(contents1))
        
        contents2 = await file2.read()
        df2 = pd.read_csv(pd.io.common.BytesIO(contents2))
        
        # Calculate campaign insights for both weeks
        campaign_analysis_week1 = {
            "overview": {
                "total_campaigns": len(df1['Campaign name'].unique()),
                "total_spend": f"£{df1['Amount spent (GBP)'].sum():.2f}",
                "total_impressions": int(df1['Impressions'].sum()),
                "total_reach": int(df1['Reach'].sum()),
                "average_cpr": f"£{df1['Cost per results'].mean():.2f}",
                "total_results": int(df1['Results'].sum())
            },
            "campaign_details": df1.groupby('Campaign name').agg({
                'Results': 'sum',
                'Impressions': 'sum',
                'Amount spent (GBP)': 'sum',
                'Cost per results': 'mean'
            }).to_dict('index'),
            "date_range": {
                "start": df1['Reporting starts'].min(),
                "end": df1['Reporting ends'].max()
            }
        }
        
        # Calculate campaign insights
        campaign_analysis = {
            "overview": {
                "total_campaigns": len(df['Campaign name'].unique()),
                "total_spend": f"£{df['Amount spent (GBP)'].sum():.2f}",
                "total_impressions": int(df['Impressions'].sum()),
                "total_reach": int(df['Reach'].sum()),
                "average_cpr": f"£{df['Cost per results'].mean():.2f}",
                "total_results": int(df['Results'].sum())
            },
            "campaign_details": df.groupby('Campaign name').agg({
                'Results': 'sum',
                'Impressions': 'sum',
                'Amount spent (GBP)': 'sum',
                'Cost per results': 'mean'
            }).to_dict('index'),
            "date_range": {
                "start": df['Reporting starts'].min(),
                "end": df['Reporting ends'].max()
            }
        }
        
        # Save the analysis results to a JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = "analysis_results"
        
        # Create directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to JSON file
        output_file = f"{output_dir}/campaign_analysis_{campaign_type.value}_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(campaign_analysis, f, indent=4)
            
        print(f"\nAnalysis saved to: {output_file}")
        
        return campaign_analysis
        
    except Exception as e:
        return {"error": str(e)}

# Main entry point
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Initializing Performance Marketing Brain on {host}:{port}")
    uvicorn.run(
        "run:app",
        host=host,
        port=port,
        reload=True
    )