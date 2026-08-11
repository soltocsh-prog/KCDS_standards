import os
import json
import urllib.request
import urllib.error
import asyncio
import time

def load_env():
    # Helper to load .env variables without external dependencies
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, val = line.split('=', 1)
                    os.environ[key.strip()] = val.strip().strip('"').strip("'")

# Load environment variables
load_env()

class KcscApiClient:
    def __init__(self):
        self.default_key = "4MLIHAe8PvbVp3r9S5LH_5KiKp-oPA5bXdhWmCRJoQ8"
        self.api_keys = []
        
        # Collect KCSC_API_KEY_1 to KCSC_API_KEY_4
        for i in range(1, 5):
            val = os.getenv(f"KCSC_API_KEY_{i}")
            if val:
                self.api_keys.append(val)
                
        # Fallback if no numbered keys are found
        if not self.api_keys:
            single_key = os.getenv("KCSC_API_KEY")
            if single_key:
                self.api_keys.append(single_key)
            else:
                self.api_keys.append(self.default_key)
                
        self.current_key_index = 0

    def get_next_api_key(self) -> str:
        if not self.api_keys:
            return self.default_key
        key = self.api_keys[self.current_key_index]
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        return key

    def get_all_kcs_metadata(self) -> dict:
        """
        Fetches the complete KCS code metadata (versions, names) from KCSC CodeList API.
        """
        api_key = self.get_next_api_key()
        url = f"https://kcsc.re.kr/OpenApi/CodeList?key={api_key}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                json_str = response.read().decode('utf-8')
                
            data = json.loads(json_str)
            metadata_map = {}
            if isinstance(data, list):
                for item in data:
                    if item.get("codeType") == "KCS":
                        raw_code = item.get("code", "")
                        normalized_code = raw_code.replace(" ", "")
                        metadata_map[normalized_code] = {
                            "version": item.get("version"),
                            "name": item.get("name"),
                            "updateDate": item.get("updateDate")
                        }
                return metadata_map
            return {}
        except Exception as e:
            print(f"Error fetching KCS code list metadata: {e}")
            return {}

    def get_kcs_document(self, code: str) -> dict:
        """
        Fetches KCS document from the KCSC OpenAPI (Synchronous fallback).
        """
        normalized_code = code.replace(" ", "")
        api_key = self.get_next_api_key()
        url = f"https://kcsc.re.kr/OpenApi/CodeViewer/KCS/{normalized_code}?key={api_key}"
        
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=8) as response:
                json_str = response.read().decode('utf-8')
                
            api_response = json.loads(json_str)
            if isinstance(api_response, list) and len(api_response) > 0:
                return api_response[0]
            elif isinstance(api_response, dict):
                return api_response
            return {}
        except Exception as e:
            print(f"Error calling KCSC API for code {code}: {e}")
            return {}

    async def get_kcs_document_async(self, code: str) -> dict:
        """
        Asynchronously fetches KCS document details from OpenAPI with round-robin key rotation,
        connection timeouts, throttling delay, and exponential backoff retry.
        """
        normalized_code = code.replace(" ", "")
        max_retries = 3
        
        # Throttling delay to avoid rate-limiting triggers
        await asyncio.sleep(0.3)
        
        for attempt in range(max_retries):
            api_key = self.get_next_api_key()
            url = f"https://kcsc.re.kr/OpenApi/CodeViewer/KCS/{normalized_code}?key={api_key}"
            
            masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "..."
            print(f"[API Call] Code: {code}, Attempt: {attempt+1}, Key: {masked_key}")
            
            try:
                # Wrap urllib request in a thread pool to avoid blocking the asyncio event loop
                def perform_request():
                    req = urllib.request.Request(url)
                    with urllib.request.urlopen(req, timeout=8) as response:
                        return response.read().decode('utf-8')
                
                json_str = await asyncio.to_thread(perform_request)
                api_response = json.loads(json_str)
                
                if isinstance(api_response, list) and len(api_response) > 0:
                    return api_response[0]
                elif isinstance(api_response, dict):
                    return api_response
                
                raise Exception("Empty or invalid API response structure")
                
            except (urllib.error.HTTPError, urllib.error.URLError, asyncio.TimeoutError, Exception) as e:
                print(f"[API Warn] Failed attempt {attempt+1} for {code} using key {masked_key}: {e}")
                if attempt == max_retries - 1:
                    raise Exception(f"All {max_retries} retries failed for {code}: {str(e)}")
                
                # Sleep time: 1s, 2s, 4s...
                sleep_time = 2 ** attempt
                await asyncio.sleep(sleep_time)

