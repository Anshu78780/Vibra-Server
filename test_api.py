"""
Test script for the Music Backend API
Run this script to test the basic functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running.")
        return False

def test_search():
    """Test the search endpoint"""
    print("\nTesting search endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/search?q=test song&limit=3")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and len(data.get('songs', [])) > 0:
                print(f"✅ Search test passed - Found {len(data['songs'])} songs")
                print(f"   First result: {data['songs'][0]['title']} by {data['songs'][0]['artist']}")
                return True
            else:
                print("❌ Search test failed - No results found")
                return False
        else:
            print(f"❌ Search test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search test error: {str(e)}")
        return False

def test_extract():
    """Test the extract endpoint"""
    print("\nTesting extract endpoint...")
    try:
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
        response = requests.post(f"{BASE_URL}/extract", 
                               json={"url": test_url},
                               headers={"Content-Type": "application/json"})
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('song'):
                song = data['song']
                print(f"✅ Extract test passed")
                print(f"   Title: {song['title']}")
                print(f"   Artist: {song['artist']}")
                print(f"   Duration: {song['duration_string']}")
                print(f"   Has audio URL: {'Yes' if song['audio_url'] else 'No'}")
                print(f"   Has thumbnail: {'Yes' if song['thumbnail'] else 'No'}")
                return True
            else:
                print("❌ Extract test failed - No song data returned")
                return False
        else:
            print(f"❌ Extract test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Extract test error: {str(e)}")
        return False

def test_homepage():
    """Test the homepage endpoint"""
    print("\nTesting homepage endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/homepage?limit=5")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                homepage_data = data['data']
                trending_music = homepage_data.get('trending_music', [])
                print(f"✅ Homepage test passed")
                print(f"   Found {len(trending_music)} trending videos")
                print(f"   Categories: {homepage_data.get('categories', [])}")
                if trending_music:
                    first_video = trending_music[0]
                    print(f"   First video: {first_video['title']} by {first_video['artist']}")
                    print(f"   Source: {first_video.get('source', 'unknown')}")
                return True
            else:
                print("❌ Homepage test failed - No data returned")
                return False
        else:
            print(f"❌ Homepage test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Homepage test error: {str(e)}")
        return False

def test_audio_url():
    """Test the audio URL endpoint"""
    print("\nTesting audio URL endpoint...")
    try:
        test_video_id = "dQw4w9WgXcQ"  # Rick Roll for testing
        response = requests.get(f"{BASE_URL}/audio/{test_video_id}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('audio_url'):
                print(f"✅ Audio URL test passed")
                print(f"   Video ID: {data['video_id']}")
                print(f"   Has audio URL: Yes")
                print(f"   URL length: {len(data['audio_url'])} characters")
                return True
            else:
                print("❌ Audio URL test failed - No audio URL returned")
                return False
        else:
            print(f"❌ Audio URL test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Audio URL test error: {str(e)}")
        return False

def test_category():
    """Test the category endpoint"""
    print("\nTesting category endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/category/pop?limit=3")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('videos'):
                videos = data['videos']
                print(f"✅ Category test passed")
                print(f"   Found {len(videos)} pop videos")
                print(f"   Category: {data.get('category')}")
                if videos:
                    first_video = videos[0]
                    print(f"   First video: {first_video['title']} by {first_video['artist']}")
                return True
            else:
                print("❌ Category test failed - No videos returned")
                return False
        else:
            print(f"❌ Category test failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Category test error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🎵 Music Backend API Test Suite")
    print("=" * 40)
    
    tests = [test_health, test_search, test_extract, test_homepage, test_audio_url, test_category]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("🎉 All tests passed! Your music backend is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs for more details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
