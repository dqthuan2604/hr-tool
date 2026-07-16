import asyncio
from app.services.file_parser import save_upload
import sys

async def test():
    print("Testing save_upload")
    try:
        res = save_upload(b"Test content", "test.txt")
        print("Success:", res)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
