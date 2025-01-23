import httpx

async def test_health():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_health()) 