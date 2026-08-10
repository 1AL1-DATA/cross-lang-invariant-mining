#[derive(Clone, PartialEq)]
pub enum Element {
    Integer(i64),
    Float(f64),
    String(String),
    List(Vec<Element>),
}

pub fn flatten(lst: &[Element]) -> Vec<Element> {
    let mut result = Vec::new();
    for item in lst {
        match item {
            Element::List(nested) => result.extend(flatten(nested)),
            other => result.push(other.clone()),
        }
    }
    result
}