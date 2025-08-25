"""
Deployment verification script
Run this to test your deployed API on Render
"""

import requests
import sys
import time

def test_deployed_api(base_url):
    """Test the deployed API endpoints"""
    print(f"🚀 Testing deployed API at: {base_url}")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Environment: {data.get('environment')}")
            print(f"   YTMusic API: {data.get('services', {}).get('ytmusic_api', 'Unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {str(e)}")
        return False
    
    # Test search endpoint
    print("\n2. Testing search endpoint...")
    try:
        response = requests.get(f"{base_url}/search?q=test&limit=2", timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('songs'):
                print(f"   ✅ Search test passed - Found {len(data['songs'])} songs")
                print(f"   First result: {data['songs'][0].get('title', 'N/A')}")
            else:
                print("   ⚠️  Search returned no results")
        else:
            print(f"   ❌ Search test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Search test error: {str(e)}")
    
    # Test homepage endpoint
    print("\n3. Testing homepage endpoint...")
    try:
        response = requests.get(f"{base_url}/homepage?limit=3", timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                trending = data['data'].get('trending_music', [])
                print(f"   ✅ Homepage test passed - Found {len(trending)} trending songs")
                if trending:
                    print(f"   First trending: {trending[0].get('title', 'N/A')}")
            else:
                print("   ⚠️  Homepage returned no data")
        else:
            print(f"   ❌ Homepage test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Homepage test error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Deployment verification completed!")
    print(f"📍 Your API is live at: {base_url}")
    print("\n📚 API Documentation:")
    print(f"   Homepage: {base_url}/")
    print(f"   Health: {base_url}/health")
    print(f"   Search: {base_url}/search?q=<query>&limit=<limit>")
    print(f"   Homepage: {base_url}/homepage?limit=<limit>")
    print(f"   Categories: {base_url}/category/<category>?limit=<limit>")
    
    return True

def main():
    """Main verification function"""
    print("🎵 Music Backend API - Deployment Verification")
    print("=" * 50)
    
    # Get the URL from user or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1].rstrip('/')
    else:
        base_url = input("Enter your Render app URL (e.g., https://your-app.onrender.com): ").strip().rstrip('/')
    
    if not base_url:
        print("❌ No URL provided")
        sys.exit(1)
    
    if not base_url.startswith('http'):
        base_url = f"https://{base_url}"
    
    print(f"🌐 Testing URL: {base_url}")
    print("⏳ Waiting for service to wake up (Render free tier sleeps after inactivity)...")
    time.sleep(3)
    
    success = test_deployed_api(base_url)
    
    if success:
        print("\n✅ All tests completed successfully!")
        print("🚀 Your Music Backend API is ready to use!")
    else:
        print("\n❌ Some tests failed. Check the Render logs for more details.")
        print("💡 Tip: Go to your Render dashboard to view real-time logs.")

if __name__ == "__main__":
    main()
