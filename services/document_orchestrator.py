import os
import json
import time
import asyncio
from db.database import get_db_connection
from services.kcsc_api_client import KcscApiClient
from services.hml_bridge import HmlOrchestrationBridge

class DocumentOrchestrator:
    def __init__(self):
        self.api_client = KcscApiClient()
        
    async def merge_documents(self, codes: list[str]) -> dict:
        """
        Asynchronously fetches the requested KCS documents (with OpenAPI caching on-the-fly)
        and merges them into a single HWP file using HmlOrchestrationBridge.
        Includes circuit breaking if API connectivity drops continuously.
        """
        codes = sorted(codes)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        merged_document = []
        warnings = []
        
        first = True
        consecutive_api_failures = 0
        circuit_broken = False
        
        # Concurrency throttle semaphore (to limit concurrent requests inside thread pool if needed)
        sem = asyncio.Semaphore(3)
        
        for code in codes:
            if circuit_broken:
                warnings.append(f"Skipped {code} due to Circuit Breaker (API connectivity issues).")
                continue
                
            try:
                # 1. Fetch metadata and cache status from DB
                cursor.execute("SELECT code, name, version, has_content, content_json FROM kcs_documents WHERE code = ?", (code,))
                row = cursor.fetchone()
                
                if not row:
                    warnings.append(f"Document code not found in catalog: {code}")
                    continue
                
                doc_data = dict(row)
                has_content = doc_data.get("has_content", 0)
                content_json = doc_data.get("content_json")
                
                sections = []
                # 2. Cache Miss -> Fetch from OpenAPI (async) and save to DB
                if not has_content or not content_json:
                    # Implement Circuit Breaker check
                    if consecutive_api_failures >= 3:
                        circuit_broken = True
                        warnings.append("API connectivity continuously failing. Circuit Breaker activated: Skipping further OpenAPI fetches.")
                        warnings.append(f"Failed to fetch content for {code}: Circuit Breaker Active")
                        continue
                        
                    try:
                        # Acquire semaphore to throttle concurrency
                        async with sem:
                            api_res = await self.api_client.get_kcs_document_async(code)
                            
                        if api_res and isinstance(api_res, dict) and "list" in api_res:
                            sections = api_res["list"]
                            # Update DB cache
                            cursor.execute(
                                "UPDATE kcs_documents SET content_json = ?, has_content = 1, updated_at = CURRENT_TIMESTAMP WHERE code = ?",
                                (json.dumps(sections, ensure_ascii=False), code)
                            )
                            conn.commit()
                            # Reset failure counter on success
                            consecutive_api_failures = 0
                        else:
                            raise Exception("Invalid or empty response structure from KCSC OpenAPI")
                    except Exception as e:
                        consecutive_api_failures += 1
                        warnings.append(f"Failed to fetch content for {code}: {str(e)}")
                        continue
                else:
                    # Cache Hit -> Parse local DB content
                    try:
                        sections = json.loads(content_json)
                    except Exception as e:
                        warnings.append(f"Failed to parse cached content for {code}: {str(e)}")
                        continue
                
                # 3. Format document sections for HmlOrchestrationBridge
                formatted_sections = []
                for sec in sections:
                    formatted_sections.append({
                        "level": sec.get("level", 4),
                        "label": sec.get("label", ""),
                        "content": sec.get("contents", "")
                    })
                
                # Build document object
                doc = {
                    "code": doc_data["code"],
                    "name": doc_data["name"],
                    "version": doc_data["version"],
                    "content_sections": formatted_sections
                }
                
                if not first:
                    merged_document.append({"type": "page_break"})
                first = False
                
                merged_document.append(doc)
                
            except Exception as e:
                warnings.append(f"Error processing document {code}: {str(e)}")
                continue
                
        conn.close()
        
        # 4. Generate HML/HWP if there are merged documents
        download_url = None
        if merged_document:
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                template_path = os.path.join(base_dir, "templates", "base_template2.hml")
                
                output_filename = f"merged_{int(time.time())}.hwp"
                output_dir = os.path.join(base_dir, "output")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, output_filename)
                
                # Run sync HML Bridge inside thread pool to prevent blocking the event loop
                def run_bridge():
                    bridge = HmlOrchestrationBridge(template_path)
                    bridge.generate_hml(merged_document, output_path)
                    
                await asyncio.to_thread(run_bridge)
                
                download_url = f"/api/kcs/download/{output_filename}"
            except Exception as e:
                warnings.append(f"Failed to generate HWP document: {str(e)}")
        
        return {
            "merged_document": merged_document,
            "warnings": warnings,
            "download_url": download_url
        }


