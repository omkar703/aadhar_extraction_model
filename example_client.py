#!/usr/bin/env python3
"""
Example client script to test the Aadhaar OCR API.

Usage:
    python example_client.py <image_path>
    
Example:
    python example_client.py aadhaar_card.jpg
"""
import sys
import json
import requests
from pathlib import Path


API_BASE_URL = "http://localhost:8000"


def check_health():
    """Check if the API is healthy and running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        response.raise_for_status()
        health_data = response.json()
        
        print("🔍 API Health Check:")
        print(f"   Status: {health_data['status']}")
        print(f"   Model Loaded: {health_data['model_loaded']}")
        print(f"   Tesseract Available: {health_data['tesseract_available']}")
        print(f"   Version: {health_data['version']}")
        print()
        
        return health_data['status'] == 'healthy'
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Cannot connect to API at {API_BASE_URL}")
        print(f"   Details: {str(e)}")
        print("\n💡 Make sure the API is running:")
        print("   docker-compose up")
        print("   OR")
        print("   ./start.sh")
        return False


def extract_aadhaar_data(image_path):
    """Extract data from an Aadhaar card image."""
    image_file = Path(image_path)
    
    # Validate file exists
    if not image_file.exists():
        print(f"❌ Error: File not found: {image_path}")
        return None
    
    # Validate file extension
    if image_file.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
        print(f"❌ Error: Invalid file format. Supported: JPG, JPEG, PNG")
        return None
    
    print(f"📤 Uploading image: {image_path}")
    
    try:
        # Open and upload the file
        with open(image_path, 'rb') as f:
            files = {'file': (image_file.name, f, 'image/jpeg')}
            response = requests.post(
                f"{API_BASE_URL}/extract",
                files=files,
                timeout=30
            )
        
        response.raise_for_status()
        result = response.json()
        
        print("\n✅ Extraction Successful!")
        print(f"⏱️  Processing Time: {result['processing_time']:.3f} seconds")
        print()
        
        # Display extracted data
        if result['data']:
            print("📋 Extracted Data:")
            for key, value in result['data'].items():
                if value:
                    print(f"   {key}: {value}")
        else:
            print("⚠️  No data extracted from the image")
        
        print()
        
        # Display detections
        if result['detections']:
            print(f"🔍 Detections ({len(result['detections'])} found):")
            for detection in result['detections']:
                label = detection['label']
                confidence = detection['confidence']
                text = detection.get('text', 'N/A')
                print(f"   • {label} (confidence: {confidence:.2f})")
                if text and text != 'N/A':
                    print(f"     Text: {text}")
        
        print()
        print("📄 Full Response:")
        print(json.dumps(result, indent=2))
        
        return result
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        try:
            error_detail = e.response.json()
            print(f"   {error_detail.get('error', 'Unknown error')}")
            if 'detail' in error_detail:
                print(f"   Details: {error_detail['detail']}")
        except:
            print(f"   {e.response.text}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request Error: {str(e)}")
        return None
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        return None


def main():
    """Main function."""
    print("=" * 60)
    print("Aadhaar Card OCR API - Example Client")
    print("=" * 60)
    print()
    
    # Check API health first
    if not check_health():
        sys.exit(1)
    
    # Check if image path is provided
    if len(sys.argv) < 2:
        print("Usage: python example_client.py <image_path>")
        print()
        print("Example:")
        print("  python example_client.py aadhaar_card.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    # Extract data
    result = extract_aadhaar_data(image_path)
    
    if result:
        print("\n" + "=" * 60)
        print("✅ Extraction Complete!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Extraction Failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
