import json
import vector_engine

def test_vector_store_linkage():
    print("Testing VectorStore linkage...")
    
    # Initialize VectorStore
    store = vector_engine.VectorStore()
    
    # Add items
    store.add_item(
        id="item1", 
        vector=[1.0, 0.0, 0.0], 
        metadata_json=json.dumps({"name": "Unit 1"})
    )
    store.add_item(
        id="item2", 
        vector=[0.0, 1.0, 0.0], 
        metadata_json=json.dumps({"name": "Unit 2"})
    )
    store.add_item(
        id="item3", 
        vector=[0.8, 0.2, 0.0], 
        metadata_json=json.dumps({"name": "Unit 3"})
    )
    
    print("Added 3 items.")
    
    # Search
    query = [1.0, 0.1, 0.0]
    results = store.search(query, k=2)
    
    print(f"Search results for {query}:")
    for id, score in results:
        print(f"  ID: {id}, Score: {score}")
    
    # Assertions
    assert len(results) == 2
    assert results[0][0] == "item1"  # [1,0,0] is closest to [1, 0.1, 0]
    assert results[1][0] == "item3"  # [0.8, 0.2, 0] is next closest

    print("Native linkage test PASSED!")

if __name__ == "__main__":
    try:
        test_vector_store_linkage()
    except Exception as e:
        print(f"Test FAILED with error: {e}")
        exit(1)
