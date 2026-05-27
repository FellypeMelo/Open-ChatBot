use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Item {
    id: String,
    vector: Vec<f32>,
    metadata: serde_json::Value,
}

#[pyclass]
struct VectorStore {
    items: HashMap<String, Item>,
}

#[pymethods]
impl VectorStore {
    #[new]
    fn new() -> Self {
        VectorStore {
            items: HashMap::new(),
        }
    }

    fn add_item(&mut self, id: String, vector: Vec<f32>, metadata_json: String) -> PyResult<()> {
        let metadata: serde_json::Value = serde_json::from_str(&metadata_json)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid JSON: {}", e)))?;
        
        let item = Item {
            id: id.clone(),
            vector,
            metadata,
        };
        
        self.items.insert(id, item);
        Ok(())
    }

    fn search(&self, query_vector: Vec<f32>, k: usize) -> PyResult<Vec<(String, f32)>> {
        // Simple brute-force cosine similarity for the stub
        let mut scores: Vec<(String, f32)> = self.items.values()
            .map(|item| {
                let score = dot_product(&query_vector, &item.vector);
                (item.id.clone(), score)
            })
            .collect();

        // Sort by score descending
        scores.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
        
        Ok(scores.into_iter().take(k).collect())
    }
}

fn dot_product(v1: &[f32], v2: &[f32]) -> f32 {
    v1.iter().zip(v2.iter()).map(|(x, y)| x * y).sum()
}

#[pymodule]
fn vector_engine(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<VectorStore>()?;
    Ok(())
}
