#[derive(Debug, Clone, PartialEq)]
pub enum ListElement {
    Integer(i64),
    Float(f64),
    String(String),
    List(Vec<ListElement>),
}

pub fn flatten(lst: Vec<ListElement>) -> Vec<ListElement> {
    let mut result = Vec::new();
    for elem in lst {
        match elem {
            ListElement::List(inner) => {
                result.extend(flatten(inner));
            }
            other => result.push(other),