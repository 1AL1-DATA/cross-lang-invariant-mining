use std::collections::HashMap;

pub fn group_by_key(pairs: Vec<(String, i32)>) -> HashMap<String, Vec<i32>> {
    let mut result: HashMap<String, Vec<i32>> = HashMap::new();
    
    for (key, value) in pairs {
        result.entry(key).or_insert_with(Vec::new).push(value);
    }
    
    result
}