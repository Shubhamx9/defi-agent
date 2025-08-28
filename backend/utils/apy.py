import requests
from typing import List, Dict

def get_top_low_yield_apy_pools() -> List[Dict]:
    """
    Fetches APY data, filters for yields <20%, and returns the top 3.
    
    Returns:
        A list of dictionaries containing the top 3 APY pools with a yield
        less than 20%, sorted in descending order of APY.
    """
    try:
        api_url = "https://yields.llama.fi/pools"
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        pools = response.json().get("data", [])

        # Filter pools with an APY less than 20%
        filtered_pools = [
            pool for pool in pools
            if "apy" in pool and pool["apy"] is not None and pool["apy"] < 20
        ]

        # Sort the filtered pools by APY in descending order
        filtered_pools.sort(key=lambda x: x["apy"], reverse=True)

        # Format and return the top 3 results
        result = []
        for pool in filtered_pools[:3]:
            result.append({
                "apy_percentage": round(pool["apy"], 2),
                "protocol": pool.get("project", "N/A"),
                "coinpair": pool.get("symbol", "N/A"),
                "chain": pool.get("chain", "N/A"),
                "tvl_usd": pool.get("tvlUsd", 0)
            })
            
        return result
        
    except Exception as e:
        return [{"error": f"Failed to fetch or process APY data: {str(e)}"}]