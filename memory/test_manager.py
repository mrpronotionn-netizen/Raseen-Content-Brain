import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.manager import MemoryManager

print("\n=== RASEEN MEMORY MANAGER TEST ===")

memory = MemoryManager()

# Test 1: Add memory
result = memory.add_memory(
    memory_type="system_test",
    title="Raseen Manager Integration Test",
    content="Testing the full memory manager engine layer.",
    source_url=None,
    status="new"
)
print("\nADD RESULT:")
print(result)

# Test 2: Check existence
exists = memory.exists("Raseen Manager Integration Test")
print("\nEXISTS RESULT:")
print(exists)

# Test 3: Search
results = memory.search("Integration")
print("\nSEARCH RESULT:")
for item in results:
    print(f"ID: {item[0]} | Type: {item[1]} | Title: {item[2]} | Status: {item[5]}")

# Test 4: Duplicate protection
duplicate = memory.add_memory(
    memory_type="system_test",
    title="Raseen Manager Integration Test",
    content="This exact title should be rejected.",
    source_url=None
)
print("\nDUPLICATE PROTECTION RESULT:")
print(duplicate)

print("\n=== MEMORY MANAGER TEST FINISHED ===")