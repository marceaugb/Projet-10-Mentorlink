import asyncio
import aiohttp
import time

URL = "http://localhost/heals/"  # Modifier si besoin
CONCURRENCY = 1000
REQUESTS = 1000

async def fetch(session, url):
    async with session.get(url) as response:
        await response.read()
        return response.status

async def bound_fetch(sem, session, url):
    async with sem:
        return await fetch(session, url)

async def run():
    sem = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        tasks = [bound_fetch(sem, session, URL) for _ in range(REQUESTS)]
        start = time.perf_counter()
        results = await asyncio.gather(*tasks)
        duration = time.perf_counter() - start
        print(f"Total: {len(results)} requests in {duration:.2f}s")
        print(f"Average latency: {duration / len(results):.4f}s")
        print(f"Status codes: { {code: results.count(code) for code in set(results)} }")

if __name__ == "__main__":
    asyncio.run(run())
