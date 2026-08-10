package main

func Flatten(lst []interface{}) []interface{} {
    var result []interface{}
    
    for _, item := range lst {
        if nested, ok := item.([]interface{}); ok {
            result = append(result, Flatten(nested)...)
        } else {
            result = append(result, item)
        }
    }
    
    return result
}